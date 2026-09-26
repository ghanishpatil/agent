cd /work/waf_chal/waf
r2 -q -e scr.color=0 -c 'aaa; s sym.__gets; pdf; s sym.main; pdf' chal 2>/dev/null
