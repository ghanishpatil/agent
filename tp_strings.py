import re
data = open('tp_files/usr__local__sbin__r9sampler','rb').read()
# ASCII strings length>=4
for m in re.finditer(rb'[\x20-\x7e]{4,}', data):
    s = m.group().decode()
    print(f'{m.start():#08x}  {s}')
