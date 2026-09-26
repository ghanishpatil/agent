#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("instance.ctf.tdho.st", port=32971, username="player", password="reyalp")

stdin, stdout, stderr = ssh.exec_command("cat /tmp/flag.txt", timeout=5)
flag = stdout.read().decode() + stderr.read().decode()

print("="*70)
print("FLAG:")
print("="*70)
print(flag)
print("="*70)

ssh.close()
