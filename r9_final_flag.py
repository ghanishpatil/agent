import os,re
# rec9 = lane1 (newer, loaded 03:14), newest generation mh=ec3e(16108)
rec9={'cf':'a68d20eb','g8':'58804bc5','mh':'ec3e','ml':'fd28d642','lc':'5e14b0ed','cr':'e2aa95907ea02d1a','o3':'cb0cf9e7'}
rec8={'cf':'f7535567','g8':'58804bc5','mh':'ec3e','ml':'990bdb03','lc':'5e14b0ed','cr':'e2aa95907ea02d1a','o3':'68f089df'}

def cands(r,label):
    print(f'--- {label} ---')
    # different 14-byte assemblies (each field as stored bytes)
    assemblies={
      'cf+g8+mh+ml':r['cf']+r['g8']+r['mh']+r['ml'],
      'cf+g8+ml+mh':r['cf']+r['g8']+r['ml']+r['mh'],
      'mh+cf+g8+ml':r['mh']+r['cf']+r['g8']+r['ml'],
      'cf+ml+g8+mh':r['cf']+r['ml']+r['g8']+r['mh'],
      'cr+ml+mh':r['cr']+r['ml']+r['mh'],
      'cr+cf+mh':r['cr']+r['cf']+r['mh'],
      'cr+g8+mh':r['cr']+r['g8']+r['mh'],
      'cr+o3+mh':r['cr']+r['o3']+r['mh'],
      'cf+g8+lc+mh':r['cf']+r['g8']+r['lc']+r['mh'],
      'g8+cf+ml+mh':r['g8']+r['cf']+r['ml']+r['mh'],
    }
    for name,hx in assemblies.items():
        if len(hx)//2==14:
            print(f'  {name:16}: HTF{{r9_{hx}}}')

cands(rec9,'rec9 lane1 newest (PRIMARY)')
cands(rec8,'rec8 lane0 newest')

# Also check img for whether any assembled candidate hex appears as a string
img=open(os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img'),'rb').read()
decoyset=set(x.decode() for x in re.findall(rb'HTF\{r9_[0-9a-f]{28}\}',img))
print('\n(is any candidate == a planted string? none should be)')
for r,lab in [(rec9,'rec9'),(rec8,'rec8')]:
    for name,hx in {'cf+g8+mh+ml':r['cf']+r['g8']+r['mh']+r['ml'],'cf+g8+ml+mh':r['cf']+r['g8']+r['ml']+r['mh']}.items():
        f='HTF{r9_%s}'%hx
        print(f'  {lab} {name}: {"PLANTED(decoy!)" if f in decoyset else "not planted (computed)"}')
