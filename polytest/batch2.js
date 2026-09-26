const fs = require("fs");
const { JSDOM } = require("jsdom");
const jquerySrc = fs.readFileSync(__dirname + "/node_modules/jquery/dist/jquery.js", "utf8");

function test(format) {
  const html = `<!DOCTYPE html><html><body>
  <form id="poly_x" data-formula="x+y">
    <input id="x_standard" name="x" value="1"><input id="y_standard" name="y" value="2">
    <input name="formula" value="x+y"><div id="template_standard" hidden>t</div>
  </form><pre id="answer"></pre></body></html>`;
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true });
  const { window } = dom;
  const s = window.document.createElement("script"); s.textContent = jquerySrc; window.document.head.appendChild(s);
  const $ = window.$;
  const form = window.document.querySelector("form");
  form.id = "poly_" + format;
  const selected = form.id.replace("poly_", "");
  let res = { format, selThrew:false, selLen:null, evalRan:false, hit:false };
  try {
    const t = $("#template_" + selected);
    res.selLen = t.length;
    if (t.length === 0) {
      window.__HIT__ = false;
      window.type_standard = function(){ return "SAFE"; };
      try {
        window.eval("(function(){ var selected=" + JSON.stringify(selected) + "; " +
                    "return eval('type_'+selected+'(this, selected)'); }).call(document.querySelector('form'))");
        res.evalRan = true; res.hit = !!window.__HIT__;
      } catch(e){ res.evalErr = e.message.split("\n")[0]; }
    }
  } catch(e){ res.selThrew = true; res.err = e.message.split("\n")[0]; }
  return res;
}

// The `.` bridge: #template_standard.CLASS is a valid selector (id + class), empty.
// In JS type_standard.PROP(...) is member access. We want to reach a function-constructor to run code.
const cands = [
  "standard.constructor",
  "standard.constructor.constructor",
  // classic: X.constructor.constructor("payload")() but parens break selector.
  // Can we use template tag? type_standard.constructor`...` — backtick not CSS-valid.
  // Try attribute-selector value to smuggle, combined with . :
  "standard.a.b.c",
  // multiple classes valid+empty; JS member chain (undefined -> throws but no parens)
  // Try to trigger via toString override? Not from here.
];
for (const c of cands) console.log(JSON.stringify(test(c)));
