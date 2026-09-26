#!/usr/bin/env python3
# The .cal per-lane files encode effective lane state. Try to match to record groups.
# Record group A (da=02,ds=08,c7=02,c8=02,cf=f7535567,o4=50460000,x3=0002)
# Record group B (da=01,ds=07,c7=01,c8=01,cf=a68d20eb,o4=803e0000,x3=0102)
for lane in (0,1):
    d=open(rf"f:\mission-git-hackss\mission-git-hackss\tp_files\var__lib__deltaforge__lane_{lane}.cal","rb").read()
    body=d[5:-2]
    print(f"lane{lane}: lanebyte={d[4]} body={list(body)}")
# rollout active slots
laneslots={0:['o4','da','c8','cr','x3','ml','lc'], 1:['o4','dx','c7','cf','g8','ml','lc']}
print("lane0 slots:",laneslots[0])
print("lane1 slots:",laneslots[1])
