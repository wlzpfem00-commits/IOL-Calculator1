# IOL Calculator v0.2.1 — Render 배포 가이드

> 연구/화면 시험 전용. **실제 환자 정보 입력·저장 금지. 실제 IOL 도수 산출 기능 없음.** 인증/권한관리 없는 공개 시험 서버입니다.

## 1. 실행 전 사전 확인
- Python 3.9 이상 / GitHub 계정 / Render 계정
- 이 프로젝트에는 실제 공식 엔진이 없고, `/api/v1/calculate` 는 모든 공식에 대해 미연결을 반환합니다.
- **GitHub 비공개(Private) 저장소**로 올리세요. 비공개 저장소도 배포한 URL이 자동 비공개가 되는 것은 아닙니다.

## 2. GitHub 올리기
- GitHub에서 새 비공개 저장소 `iol-calculator` 생성
- 이 폴더의 파일과 폴더(`render.yaml`, `www`, `server` 포함)를 저장소 최상위에 업로드
- 환자 정보, 비밀번호, API 키, `.env` 파일은 업로드하지 마세요.

## 3. Render 배포
1. https://dashboard.render.com/ 접속 → New → Blueprint 선택
2. GitHub 저장소를 연결하고 `render.yaml`을 사용하여 배포
3. 배포 시 서비스 이름·요금제·지역을 확인합니다. render.yaml은 `free` 시험 요금제입니다. 테스트 외 용도 금지.
4. 배포 완료 후 Render에서 받은 `https://<service>.onrender.com` 주소를 확인합니다.
5. `https://<service>.onrender.com/api/v1/health` 접속, `status:ok` / `clinicalReady:false` 확인
6. `https://<service>.onrender.com` 접속 → 설정 → 서버 주소 비움 → 서버 연결 확인
7. **가상 계측값만** 입력해 계산 요청 테스트. 결과는 미연결로 나와야 정상.

### Blueprint 대신 수동 생성
- Render New → Web Service → 저장소 연결
- Runtime: Python, Root Directory: repository root
- Build Command: `echo "No dependencies required"`
- Start Command: `python server/main.py`
- Environment Variables: `IOL_HOST=0.0.0.0`, `PYTHON_VERSION=3.12.8`
- Health Check Path: `/api/v1/health`
- Python 서버는 Render의 `PORT` 환경변수를 자동으로 사용합니다.

## 4. PC와 모바일 연동
- 웹은 Render URL로 열면 웹과 API가 같은 호스트를 쓰므로 서버 주소 설정을 비워둡니다.
- Electron/Capacitor의 로컬 설치형 빌드에서는 설정에서 Render의 `https://...onrender.com` 주소를 입력합니다.
- 앱의 다른 출처에서 브라우저 CORS 요청을 보내면 Render 환경변수 `IOL_ALLOWED_ORIGINS`에 필요한 정확한 Origin을 쉼표로 구분해 지정합니다. 출처 허용만으로 API 인증이 되는 것은 아닙니다.
- Android/iOS 앱 빌드·스토어 제출은 별도 단계입니다. 이 프로젝트만으로 앱이 스토어에 게시되는 것은 아닙니다.

## 5. 업데이트
- 웹/서버 코드를 수정 → GitHub에 변경사항 커밋 및 푸시 → Render 자동 배포 여부 확인
- Git 변경 전후 `/api/v1/health`와 가상 계측값 API 회귀 시험 수행
- 웹 페이지 업데이트 시 `www/service-worker.js`의 캐시 버전 변경
- API 계약 변경 시 `/api/v1` 버전 호환성 유지/마이그레이션

## 6. 실사용 전 보안·의료 검증 필수
- 인증/권한 분리, 속도 제한, 감사 로그, 보안 관제, 개인정보 처리 정책 및 암호화 저장
- 로컬스토리지에 환자 신원정보가 들어갈 수 있으므로, 실환자 데이터 절대 입력 금지
- 의사 이름·환자 이름/ID는 API 전송되지 않도록 현재 구성됨. **안구 계측값은 외부 클라우드로 전송됨.**
- 렌즈 제조사·모델 및 공식별 상수 검증, 라이선스, 기준값 회귀시험, 임상 검증, 의료기기법상 허가·신고 등 해당 요건 검토
- Render 무료 인스턴스는 15분 비활성 시 절전 및 재가동 지연 발생 가능. 운영용에 부적합

관련 문서: https://render.com/docs/web-services , https://render.com/docs/blueprint-spec , https://render.com/docs/free
