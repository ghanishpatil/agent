import urllib.request, io, zipfile, os

url = "https://master-platform-bucket.s3.us-east-1.amazonaws.com/challenges/c5b3094a-4955-4ee4-827c-ae3860adbfd9/public.zip"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
raw = urllib.request.urlopen(req, timeout=60).read()
print("bytes:", len(raw), "head:", raw[:16])
z = zipfile.ZipFile(io.BytesIO(raw))
print("members:", [i.filename for i in z.infolist()])
os.makedirs("jail_chal", exist_ok=True)
for i in z.infolist():
    if i.is_dir():
        continue
    try:
        data = z.read(i.filename, pwd=b"infected")
    except Exception as e:
        print("FAIL", i.filename, e); continue
    dst = os.path.join("jail_chal", i.filename.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)
    print("wrote", dst, len(data))
print("DONE")
