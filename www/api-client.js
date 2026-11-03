'use strict';
// No names, patient IDs, or doctor names are transmitted in requests.
window.IOL_API={
  baseUrl: '',
  setBase(url){
    const normalized=url.trim().replace(/\/+$/,'');
    if(normalized && !/^https:\/\//i.test(normalized) && !/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(normalized)) throw Error('원격 서버는 HTTPS 주소가 필요합니다.');
    this.baseUrl=normalized;
  },
  async request(path,options={}){
    const controller=new AbortController();
    const timeout=setTimeout(()=>controller.abort(),12000);
    try{
      const response=await fetch(this.baseUrl+path,{...options,signal:controller.signal,cache:'no-store'});
      const result=await response.json();
      if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
      return result;
    }finally{clearTimeout(timeout)}
  },
  health(){return this.request('/api/v1/health')},
  calculate(form){
    const eyes={};
    for(const side of ['od','os']){
      const values=form.eyes[side];
      if(!['al','k1','k2','acd'].some(k=>values[k]!==''))continue;
      const obj={};
      for(const [key,value] of Object.entries(values))if(value!=='')obj[key]=Number(value);
      obj.targetRefraction=Number(form[side==='od'?'targetOD':'targetOS']);
      eyes[side]=obj;
    }
    const constant={type:form.constantType};
    if(form.lensFactor!=='')constant.lensFactor=Number(form.lensFactor);
    if(form.aConstant!=='')constant.aConstant=Number(form.aConstant);
    return this.request('/api/v1/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({apiVersion:'v1',eyes,formulas:form.formulas,constant})});
  }
};
