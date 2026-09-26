t = open("/work/bundle.js", encoding="utf-8").read()
i = t.find("function writeAnswer(")
j = t.find("var jquery$1")
print("i=",i,"j=",j, "len=", len(t))
if i!=-1:
    end = j if (j!=-1 and j>i) else i+3000
    print(t[i:end])
