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
        w.__run.call(form, sel);
        r.pwn = !!w.__P__;
      } catch (e) { r.ev = e.message.split("\n")[0]; }
    }
  } catch (e) { r.se = e.message.split("\n")[0]; }
  return r;
}

// Reflect.apply / .call double invocation. Free call: X(this, selected).
// If X = Function.prototype.call and we set it up so X(this, selected) invokes something running code.
// Function.prototype.call.call(F, thisArg, ...args) -> F(...args) with F's this=thisArg.
//   Here X(this, selected) = call.call? no, only 2 args.
// Consider X = eval? not reachable. X = setTimeout? not reachable via type_standard.
//
// Quoted attr lets us set a computed key = ANY string, e.g. "constructor". Build chain via brackets:
//   type_standard["constructor"]["constructor"] = Function ; then ["call"] ; the free call:
//   Function.call(this=form, selected) = Function(selected) -> fn (not run).  same wall.
//
// The ONLY way to RUN in one call with poison arg1 is to swallow arg1 as thisArg (.call) AND have the
// target be a string-executor. Reachable string-executor with (thisArg, codeString) => runs code:
//   NONE from Function. BUT: from `this`(form) we can reach window: form.ownerDocument.defaultView.
//   However base of chain is type_<format>, and `this`(form) is only arg1/thisArg.
//   With .call, thisArg=form. Inside a function, `this`=form. If target fn uses `this` to eval? no builtin.
//
// LAST: Reflect? not reachable. 
// Verdict test: confirm quoted-attr computed-key chain reaches Function and that we still can't invoke.
const cands = [
  'standard["constructor"]',                    // computed key via quoted attr? JS: type_standard["constructor"]
  'standard[a="constructor"]',                  // a="constructor" then key -> type_standard["constructor"]? no, [a="c"] = attr
];
for (const c of cands) console.log(JSON.stringify(c), "=>", JSON.stringify(test(c)));
