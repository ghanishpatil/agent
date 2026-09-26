import ast, math
data = open("data.txt").read()
Y = ast.literal_eval(data.strip().splitlines()[0])
print("len Y", len(Y))
print("max Y", max(Y), "bits", math.log2(max(Y)))
print("min Y", min(Y), "bits", math.log2(min(Y)))
B=2**48
print("max a >= ", max(Y)*B, "bits", math.log2(max(Y)*B))
print("2^128", 2**128)
print("2^128-2^48", 2**128-2**48)
print("2^128-2^50", 2**128-2**50)
print("(2^128-2^50)>>48 =", (2**128-2**50)>>48)
print("(2^128-2^48)>>48 =", (2**128-2**48)>>48)
print("2^80 =", 2**80)
# p>>48 is in [ (2^128-2^50)>>48, (2^128-2^48)>>48 ]
# max Y must be < p>>48 roughly
