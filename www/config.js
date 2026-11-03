// 사용자 설정 파일: 항목/공식/범위는 여기서 수정합니다.
window.IOL_CONFIG = {
  version: '0.2.0',
  formulas: ['SRK/T','Hoffer Q','Haigis','Holladay 1','Barrett Universal II','Kane'],
  initialFormulas: ['SRK/T','Hoffer Q','Barrett Universal II'],
  measurements: [
    {key:'al', label:'Axial Length (AL)', unit:'mm', min:12,max:38,step:0.01,required:true},
    {key:'k1', label:'Measured K1', unit:'D', min:30,max:60,step:0.01,required:true},
    {key:'k2', label:'Measured K2', unit:'D', min:30,max:60,step:0.01,required:true},
    {key:'acd', label:'Optical ACD', unit:'mm', min:0,max:6,step:0.01,required:true},
    {key:'refraction', label:'Refraction', unit:'D', min:-10,max:10,step:0.25,required:false,default:'0'},
    {key:'lt', label:'Lens Thickness (LT)',unit:'mm',min:2,max:8,step:0.01,required:false,optional:true},
    {key:'wtw',label:'WTW',unit:'mm',min:8,max:14,step:0.01,required:false,optional:true}
  ]
};
