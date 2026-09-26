const { JSDOM } = require("jsdom");
const dom = new JSDOM(`<!DOCTYPE html><body><div id="a"></div></body>`);
console.log("jsdom window?", !!dom.window, "document?", !!dom.window.document);
try {
  const jq = require("jquery");
  console.log("jquery type:", typeof jq, "has fn?", !!(jq && jq.fn));
  const $ = (typeof jq === "function" && !jq.fn) ? jq(dom.window) : jq;
  console.log("$ type:", typeof $);
  console.log("find #a length:", $("#a", dom.window.document).length);
  console.log("jQuery version:", ($.fn && $.fn.jquery));
} catch (e) {
  console.log("ERR:", e.message);
}
