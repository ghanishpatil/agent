# Recover using the exact ekv.py logic. secret and the stored ints come straight from the pickle.
secret = 437985254893270892437507894263543897032459087345980732450987234590873425980734520987234598723459823498345098

stored = {
 'the three digits on the back of my credit card': 437985254893270892437507894263543897032459087345980732450987234590873425980734520987234598723459823495187645,
 'an album you should listen to': 437985254893270892437507894263543897032459087345980732450987234590873426370746113257083238202997617224898286,
 'the flag': 437985254893270892437507895664257842590059651754668441751575962767488575336236097289980093935356811605893111,
 # 'admin password for the scoreboard' value was truncated out of the .part file
}

def decrypt(num_xored):
    num = num_xored ^ secret
    return num.to_bytes(-(num.bit_length() // -8), 'big').decode()

for k, v in stored.items():
    try:
        print(f"{k!r:50} -> {decrypt(v)!r}")
    except Exception as e:
        print(f"{k!r:50} -> ERROR {type(e).__name__}: {e}")

print()
print("FLAG:", decrypt(stored['the flag']))
