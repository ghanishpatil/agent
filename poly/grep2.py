import re
t = open("/work/bundle.js", encoding="utf-8").read()
for kw in ["type_", "globalEval", "new Function", "Function(", "eval(", "import(",
           "setTimeout", "setInterval", "= window.", "jQuery", "\\$(", "constructor",
           "srcdoc", "innerHTML", "outerHTML", "insertAdjacent", "document.write",
           "location", "\\.href", "postMessage", "atob", "decodeURIComponent"]:
    idxs = [m.start() for m in re.finditer(kw, t)]
    # focus on app tail (after last 'var jquery')
    tail = t.rfind("ReactDOM.createRoot")
    appstart = t.find("function writeAnswer(")
    app_hits = [i for i in idxs if i >= appstart-200]
    print(f"### {kw!r}: total {len(idxs)}, in-app {len(app_hits)}")
    for i in app_hits[:6]:
        print("   ", repr(t[max(0,i-50):i+70]))
