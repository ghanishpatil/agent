import socket, ssl, sys, time

HOST = "a1376d496be7342c.chal.ctf.ae"
PORT = 443

def send_expr(expr, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    raw = socket.create_connection((HOST, PORT), timeout=timeout)
    s = ctx.wrap_socket(raw, server_hostname=HOST)
    s.settimeout(timeout)
    buf = b""
    # read prompt "~ "
    try:
        while b"~" not in buf:
            d = s.recv(4096)
            if not d: break
            buf += d
    except Exception:
        pass
    s.sendall(expr.encode() + b"\n")
    out = b""
    try:
        while True:
            d = s.recv(4096)
            if not d: break
            out += d
    except Exception:
        pass
    s.close()
    return (buf + out).decode(errors="replace")

if __name__ == "__main__":
    expr = sys.argv[1] if len(sys.argv) > 1 else "hint_B"
    print("EXPR:", expr)
    print(send_expr(expr))
