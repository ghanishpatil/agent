const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const purifySrc = fs.readFileSync(path.join(__dirname,'node_modules','dompurify','dist','purify.min.js'),'utf8');

const APP_HTML = (bodyRaw) => `<!doctype html><html><head></head><body>
<main id="viewer">
  <article class="note"><h1 id="v-title"></h1><div id="note"></div></article>
  <aside class="vault"><h3>Your vault</h3><div id="vault" aria-hidden="true"></div></aside>
</main>
<script>${purifySrc}</script>
<script>
  try {
    window.__dp = typeof DOMPurify;
    localStorage.setItem("flag","NNS{FAKE_LOCAL_FLAG_1234}");
    const raw = ${JSON.stringify(bodyRaw)};
    const c = DOMPurify.sanitize(raw, {FORBID_TAGS:["style"], RETURN_DOM_FRAGMENT:true});
    document.getElementById("note").replaceChildren(c);
    const n = localStorage.getItem("flag");
    if(n){ document.getElementById("vault").textContent = n; }
    window.__ok = true;
  } catch(e){ window.__err = ''+e; }
</script>
</body></html>`;

(async () => {
  const http = require('http');
  const hits = [];
  const srv = http.createServer((req,res)=>{ hits.push(req.url); res.end('ok'); });
  await new Promise(r=>srv.listen(9999,r));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', m=>console.log('CONSOLE:', m.text()));
  page.on('pageerror', e=>console.log('PAGEERR:', e.message));
  const body = '<img id="vault" src="http://127.0.0.1:9999/hit_start"><p>hi</p>';
  await page.setContent(APP_HTML(body), {waitUntil:'load'}).catch(e=>console.log('err',e.message));
  await page.waitForTimeout(600);
  const info = await page.evaluate(()=>({
    dp: window.__dp, ok: window.__ok, err: window.__err,
    vtag: document.getElementById('vault') && document.getElementById('vault').tagName,
    vhtml: document.getElementById('vault') && document.getElementById('vault').outerHTML,
    note: document.getElementById('note').innerHTML
  }));
  console.log('info:', JSON.stringify(info,null,2));
  console.log('hits:', JSON.stringify(hits));
  await browser.close(); srv.close();
})();
