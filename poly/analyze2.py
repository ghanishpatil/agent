t = open("/work/bundle.js", encoding="utf-8").read()
import re

for kw in ['poly_', 'template_', 'data-formula', 'dataset', 'getAttribute',
           '.html(', '.append(', '.on("submit"', "on('submit'", 'submit',
           'eval(', 'Function(', 'new Function', '$(', 'jQuery(', '#answer',
           'requestSubmit', 'addEventListener', 'find(', 'attr(']:
    idxs = [m.start() for m in re.finditer(re.escape(kw), t)]
    # Only show hits NOT inside the giant jQuery lib body if too many; cap
    print(f"\n##### {kw!r}: {len(idxs)} hits")
    for i in idxs[:6]:
        print("  ...", repr(t[max(0,i-90):i+90]))
