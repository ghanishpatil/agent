const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');
const purifySrc = fs.readFileSync(path.join(__dirname,'node_modules','dompurify','dist','purify.min.js'),'utf8');

// Real-chromium test: does any payload EXECUTE js (hit /XSS) after replaceChildren?
const APP_HTML = (bodyRaw) => `<!doctype html><html><head></head><body>
<div id="note"></div>
<script>${purifySrc}</script>
<script>
  const raw = ${JSON.stringify(bodyRaw)};
  const c = DOMPurify.sanitize(raw, {FORBID_TAGS:["style"], RETURN_DOM_FRAGMENT:true});
  document.getElementById("note").replaceChildren(c);
</script>
</body></html>`;

const payloads = {
  'svg_style': '<svg><style>@import url(http://127.0.0.1:9999/svgstyle)</style></svg>',
  'form_action_clobber': '<form><input name=attributes></form>',
  'mglyph': '<math><mtext><mglyph><style>*{background:url(http://127.0.0.1:9999/mglyph)}</style></mglyph></mtext></math>',
  'noscript_style': '<noscript><style>@import url(http://127.0.0.1:9999/noscriptstyle)</style></noscript>',
  'select_style': '<select><style>@import url(http://127.0.0.1:9999/selstyle)</style></select>',
  'img_style_bg': '<img src=x style="background:url(http://127.0.0.1:9999/imgbg)">',
  'div_bg': '<div style="background-image:url(http://127.0.0.1:9999/divbg)">x</div>',
};

(async () => {
  const hits = [];
  const srv = http.createServer((req,res)=>{
    hits.push(req.url);
    if(req.url.startsWith('/page')){
      const which = decodeURIComponent(req.url.split('=')[1]);
      res.setHeader('Content-Type','text/html');
      res.end(APP_HTML(payloads[which]));
    } else res.end('ok');
  });
  await new Promise(r=>srv.listen(9999,r));
  const browser = await chromium.launch();
  for (const name of Object.keys(payloads)) {
    const page = await browser.newPage();
    const before = hits.length;
    await page.goto('http://127.0.0.1:9999/page?p='+encodeURIComponent(name),{waitUntil:'networkidle'}).catch(()=>{});
    await page.waitForTimeout(400);
    const note = await page.evaluate(()=>document.getElementById('note').innerHTML);
    console.log('\n==',name,'==');
    console.log('note:', note.slice(0,200));
    console.log('hits:', JSON.stringify(hits.slice(before).filter(u=>!u.startsWith('/page'))));
    await page.close();
  }
  await browser.close(); srv.close();
})();
