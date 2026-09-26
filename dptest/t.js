
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);
console.log('version', DOMPurify.version);

const payloads = [
  '<img src=x onerror="fetch(1)">',
  '<svg><script>alert(1)</script></svg>',
  '<a href="javascript:alert(1)">x</a>',
  '<iframe src="javascript:alert(1)"></iframe>',
  '<img src=x id=vault>',
  '<form id=note><input name=innerHTML></form>',
  '<style>@import url(x)</style>',
  '<div style="background:url(http://evil/x)">y</div>',
  '<link rel=stylesheet href=http://evil/x>',
  '<svg><animate onbegin=alert(1)>',
  '<math><mtext><style>@import"x"</style></mtext></math>',
  '<img src=1 srcset=x>',
  '<template><img src=x onerror=alert(1)></template>',
  '<noscript><p title="</noscript><img src=x onerror=alert(1)>">',
];
for (const p of payloads) {
  const out = DOMPurify.sanitize(p, {FORBID_TAGS:['style'], RETURN_DOM_FRAGMENT:true});
  const div = window.document.createElement('div');
  div.appendChild(out.cloneNode(true));
  console.log(JSON.stringify(p) + '  =>  ' + JSON.stringify(div.innerHTML));
}
