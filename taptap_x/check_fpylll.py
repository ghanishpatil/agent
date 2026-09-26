try:
    import fpylll
    from fpylll import IntegerMatrix, LLL
    print("fpylll OK", fpylll.__version__)
except Exception as e:
    print("FAIL", e)
