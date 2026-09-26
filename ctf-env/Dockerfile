# CTF Solving Environment — Linux toolchain for rev / pwn / crypto / forensics / web / stego
# Build:  docker build -t ctf-env ./ctf-env
# Run:    docker run -it --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env
# (mounts the whole workspace at /work so the agent + you share files)

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# ---------------------------------------------------------------------------
# 1. Base system + build tooling
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make cmake gdb \
    git curl wget file xxd bsdmainutils \
    python3 python3-pip python3-dev python3-venv pipx \
    unzip p7zip-full zip tar \
    vim less jq ripgrep \
    ca-certificates gnupg \
    netcat-openbsd nmap dnsutils iputils-ping socat openssl \
    libssl-dev libffi-dev \
    binutils patchelf \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# 2. Reverse engineering / pwn
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    radare2 \
    ltrace strace \
    gdb-multiarch \
    qemu-user qemu-user-static \
    libc6-i386 \
    && rm -rf /var/lib/apt/lists/*

# pwndbg (gdb enhancement) — clone + install
RUN git clone --depth 1 https://github.com/pwndbg/pwndbg /opt/pwndbg \
    && cd /opt/pwndbg && ./setup.sh || true

# ---------------------------------------------------------------------------
# 3. Forensics / stego
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    binwalk foremost \
    steghide \
    exiftool libimage-exiftool-perl \
    sleuthkit \
    tcpdump tshark \
    poppler-utils \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# zsteg (Ruby) for PNG/BMP stego
RUN apt-get update && apt-get install -y --no-install-recommends ruby ruby-dev \
    && gem install zsteg --no-document || true \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# 4. Web / recon
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    hydra \
    hashcat john \
    && rm -rf /var/lib/apt/lists/*

# gobuster + ffuf (Go tools via apt where available)
RUN apt-get update && apt-get install -y --no-install-recommends gobuster ffuf || true \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# 5. Python CTF libraries (the workhorses)
# ---------------------------------------------------------------------------
RUN pip3 install --no-cache-dir \
    pwntools \
    pycryptodome \
    gmpy2 \
    sympy \
    z3-solver \
    requests \
    beautifulsoup4 \
    capstone \
    unicorn \
    keystone-engine \
    ropgadget \
    angr \
    pillow \
    numpy \
    scipy \
    oletools \
    pyshark \
    roman \
    base58 \
    pyjwt \
    || pip3 install --no-cache-dir \
    pwntools pycryptodome gmpy2 sympy z3-solver requests beautifulsoup4 \
    capstone unicorn ropgadget pillow numpy oletools pyjwt

# one_gadget (Ruby)
RUN gem install one_gadget --no-document || true

# RsaCtfTool — automated RSA attacks (newer src/ layout; install as a package → `RsaCtfTool` on PATH)
RUN git clone --depth 1 https://github.com/RsaCtfTool/RsaCtfTool /opt/RsaCtfTool \
    && cd /opt/RsaCtfTool \
    && pip3 install --no-cache-dir -r requirements.txt || true \
    && pip3 install --no-cache-dir -e . || true

# ---------------------------------------------------------------------------
# 6. Reference repos (cloned so the agent can grep them OFFLINE)
# ---------------------------------------------------------------------------
RUN mkdir -p /opt/refs && cd /opt/refs \
    && git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git || true \
    && git clone --depth 1 https://github.com/danielmiessler/SecLists.git || true \
    && git clone --depth 1 https://github.com/GTFOBins/GTFOBins.github.io.git GTFOBins || true \
    && git clone --depth 1 https://github.com/LOLBAS-Project/LOLBAS.git || true

WORKDIR /work
CMD ["/bin/bash"]
