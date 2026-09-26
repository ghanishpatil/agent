src=open("chall.py").read()
# the commented block after the code contains Y (list) and ct hex
import re
m=re.search(r"'''\s*(\[.*?\])\s*([0-9a-f]+)\s*'''", src, re.S)
Ytxt=m.group(1); ct=m.group(2)
open("data.txt","w").write(Ytxt+"\n"+ct+"\n")
print("Y len", Ytxt.count(",")+1, "ct len(hex)", len(ct), "ct bytes", len(ct)//2)
