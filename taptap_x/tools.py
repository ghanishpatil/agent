import importlib
for m in ["fpylll","sage","sympy","z3","Crypto","numpy","olll","flatter"]:
    try:
        mod=importlib.import_module(m)
        print("OK", m, getattr(mod,"__version__","?"))
    except Exception as e:
        print("NO", m, str(e)[:60])
import shutil
for b in ["sage","flatter","fplll"]:
    print("bin", b, shutil.which(b))
