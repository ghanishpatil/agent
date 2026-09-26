const { JSDOM } = require("jsdom");
const dom = new JSDOM("<!DOCTYPE html><form id='poly_standard'><div id='template_standard'></div></form>", { url: "https://polynomial.secso.cc/" });
global.window = dom.window;
global.document = dom.window.document;
const $ = require("jquery");
console.log("jQuery version:", $.fn.jquery);
console.log("template match:", $("#template_standard").length);
function trySel(s){ try { return "OK len="+$(s).length; } catch(e){ return "THROW: "+e.message.slice(0,60); } }
for (const s of ["#template_,alert", "#template_,alert(1)", "#template_,fetch(1)", "#template_,eval.call", "#template_+eval.call", "#template_:not(x)", "#template_,x:contains(y)"]) {
  console.log(s, "=>", trySel(s));
}
