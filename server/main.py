"""IOL Calculator API scaffold. Research-only. NO clinical calculation code."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'www'
FORMULAS = ('SRK/T', 'Hoffer Q', 'Haigis', 'Holladay 1', 'Barrett Universal II', 'Kane')
LIMITS = {'al': (12, 38), 'k1': (30, 60), 'k2': (30, 60), 'acd': (0, 6), 'refraction': (-10, 10), 'lt': (2, 8), 'wtw': (8, 14)}
ALLOWED_ORIGINS = {s.strip() for s in os.getenv('IOL_ALLOWED_ORIGINS', '').split(',') if s.strip()}
MIME = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.json':'application/json','.webmanifest':'application/manifest+json','.png':'image/png'}

class Handler(BaseHTTPRequestHandler):
    server_version = 'IOLPrototype/0.2'

    def _cors(self):
        origin = self.headers.get('Origin', '')
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def respond(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/v1/health':
            return self.respond(200, {'status':'ok','apiVersion':'v1','service':'iol-calculator','clinicalReady':False})
        if path == '/api/v1/capabilities':
            return self.respond(200, {'apiVersion':'v1','formulas':[{'name':x,'available':False,'reason':'Not validated or licensed for clinical computation'} for x in FORMULAS]})
        if path.startswith('/api/'):
            return self.respond(404, {'error':'unknown_endpoint'})
        if path == '/': path = '/index.html'
        target = (ROOT / path.lstrip('/')).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            return self.respond(404, {'error':'not_found'})
        data = target.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(target.suffix, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control','no-store' if target.name in ('config.js','app.js','api-client.js','service-worker.js') else 'public, max-age=300')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/v1/calculate':
            return self.respond(404, {'error':'unknown_endpoint'})
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size <= 16384:
                return self.respond(413, {'error':'invalid_payload_size'})
            req = json.loads(self.rfile.read(size))
            if not isinstance(req,dict) or set(req) - {'apiVersion','eyes','formulas','constant'}:
                return self.respond(400, {'error':'invalid_schema','message':'Only non-identifying computation fields are accepted'})
            if req.get('apiVersion') != 'v1':
                return self.respond(400, {'error':'unsupported_api_version'})
            fs = req.get('formulas')
            if not isinstance(fs,list) or not fs or len(fs)>len(FORMULAS) or any(x not in FORMULAS for x in fs) or len(set(fs))!=len(fs):
                return self.respond(422, {'error':'invalid_formulas'})
            eyes = req.get('eyes')
            if not isinstance(eyes,dict) or not eyes or set(eyes)-{'od','os'}:
                return self.respond(422, {'error':'invalid_eyes'})
            for side, eye in eyes.items():
                if not isinstance(eye,dict) or set(eye)-set(LIMITS)-{'targetRefraction'}:
                    return self.respond(422, {'error':'invalid_eye_fields','eye':side})
                for key in ('al','k1','k2','acd','targetRefraction'):
                    if key not in eye: return self.respond(422,{'error':'missing_required_measurement','field':key,'eye':side})
                for key, val in eye.items():
                    if not isinstance(val,(int,float)) or isinstance(val,bool) or abs(val)>100000:
                        return self.respond(422, {'error':'measurement_must_be_numeric','field':key,'eye':side})
                    if key in LIMITS and not LIMITS[key][0] <= val <= LIMITS[key][1]:
                        return self.respond(422, {'error':'measurement_out_of_range','field':key,'eye':side})
                    if key=='targetRefraction' and not -20<=val<=20:
                        return self.respond(422, {'error':'target_out_of_range','eye':side})
            const = req.get('constant',{})
            if not isinstance(const,dict) or set(const)-{'type','lensFactor','aConstant'}:
                return self.respond(422, {'error':'invalid_constant'})
            # Return structured non-results: do not fabricate IOL powers.
            results = {eye: [{'formula':f,'status':'unavailable','iolPower':None,'predictedRefraction':None,'reason':'Verified calculation implementation not connected'} for f in fs] for eye in eyes}
            return self.respond(200, {'apiVersion':'v1','clinicalReady':False,'results':results,'message':'Server connected. Formula calculation remains disabled until verified.'})
        except (ValueError,UnicodeError,TypeError):
            return self.respond(400, {'error':'malformed_json'})

if __name__ == '__main__':
    host = os.getenv('IOL_HOST','127.0.0.1')
    port = int(os.getenv('PORT', os.getenv('IOL_PORT', '8000')))
    print(f'IOL prototype server: http://{host}:{port} (NOT FOR CLINICAL USE)', flush=True)
    ThreadingHTTPServer((host,port), Handler).serve_forever()
