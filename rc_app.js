(() => {
  "use strict";

  const popup = document.getElementById("popup");
  const wrapper = document.getElementById("popup-wrapper");
  const header = document.getElementById("popup-header");
  const instruction = document.getElementById("challenge-instruction");
  const title = document.getElementById("challenge-title");
  const format = document.getElementById("challenge-format");
  const input = document.getElementById("challenge-input");
  const submit = document.getElementById("submit-button");
  const opener = document.getElementById("open-challenge");
  const timerValue = document.getElementById("timer-value");
  const timerProgress = document.getElementById("timer-progress");
  const requiredCorrect = 10;
  let duration = 8;
  let numCorrect = 0;
  let state = "closed";
  let deadline = 0;
  let frame = 0;
  let answer;
  let pi;

  function printFlag(){if(state!==String.fromCharCode(99,111,109,112,108,101,116,101)||!Number.isInteger(numCorrect)||numCorrect<requiredCorrect||!(requiredCorrect>0))return false;const _0x91=[0x25,0x71,0x64,0xbc,0xc5,0x62,0xdc,0xbe,0x6d,0x45,0x63,0x67,0xd7,0xc8,0xea,0x12,0x59,0x8a,0x38,0xd0,0xe7,0x4a,0xe1,0x9b,0x57,0xf8,0x18,0x35,0x92,0x61,0xb0,0x92,0xea,0xd8,0xa6,0x08,0x2d,0x6b,0xc6,0x83,0x2f,0xb2,0x4f,0xf7,0x4d,0x5d,0x44,0x3a,0x58,0x45];let _0x42=0x35+state.length*0x11;const _0x17=new TextDecoder().decode(Uint8Array.from(_0x91,(_0x6a,_0x2b)=>{_0x42=(_0x42*0x21+_0x2b+0x11)&0xff;return _0x6a^_0x42}));document.getElementById("flag").textContent=_0x17;document.getElementById("flag-result").hidden=false;console.log(_0x17);return true}

  function generatePi(n) {
    let i = 1n;
    let x = 3n * 10n ** BigInt(n + 20);
    let result = x;
    while (x > 0n) {
      x = (x * i) / ((i + 1n) * 4n);
      result += x / (i + 2n);
      i += 2n;
    }
    return String(result / 10n ** 20n);
  }

  function sha256(text) {
    const bytes = new TextEncoder().encode(text);
    const size = Math.ceil((bytes.length + 9) / 64) * 64;
    const data = new DataView(new ArrayBuffer(size));
    bytes.forEach((byte, i) => data.setUint8(i, byte));
    data.setUint8(bytes.length, 0x80);
    data.setUint32(size - 8, Math.floor(bytes.length / 0x20000000));
    data.setUint32(size - 4, bytes.length * 8);
    const h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    const k = [
      0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ];
    const rotate = (x, n) => (x >>> n) | (x << (32 - n));
    const w = new Uint32Array(64);
    for (let offset = 0; offset < size; offset += 64) {
      for (let i = 0; i < 16; i++) w[i] = data.getUint32(offset + i * 4);
      for (let i = 16; i < 64; i++) {
        const a = w[i - 15], b = w[i - 2];
        const s0 = rotate(a, 7) ^ rotate(a, 18) ^ (a >>> 3);
        const s1 = rotate(b, 17) ^ rotate(b, 19) ^ (b >>> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
      }
      let [a, b, c, d, e, f, g, hh] = h;
      for (let i = 0; i < 64; i++) {
        const s1 = rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25);
        const t1 = (hh + s1 + ((e & f) ^ (~e & g)) + k[i] + w[i]) | 0;
        const s0 = rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22);
        const t2 = (s0 + ((a & b) ^ (a & c) ^ (b & c))) | 0;
        hh = g; g = f; f = e; e = (d + t1) | 0;
        d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      [a, b, c, d, e, f, g, hh].forEach((v, i) => { h[i] = (h[i] + v) | 0; });
    }
    return h.map(v => (v >>> 0).toString(16).padStart(8, "0")).join("");
  }

  function integral(max, fn) {
    const dx = max / 10000;
    let x = 0, y = fn(0), sum = 0;
    for (let i = 0; i < 10000; i++) {
      const nextX = x + dx;
      const nextY = fn(nextX);
      sum += (y + nextY) * dx / 2;
      x = nextX;
      y = nextY;
    }
    return sum;
  }

  function generateChallenge() {
    const type = Math.floor(Math.random() * 8);
    let n;
    switch (type) {
      case 0:
        n = Math.floor(Math.random() * 100000000);
        return ["Please enter the square root of", n, "to 5 decimal places", Math.sqrt(n).toFixed(5)];
      case 1:
        n = Math.round(Math.random() * 9000 + 1000);
        pi ??= generatePi(10000);
        return ["Please enter the sum of", `the first ${n} digits of pi`, "after the decimal point",
          [...pi.slice(1, n + 1)].reduce((sum, digit) => sum + Number(digit), 0)];
      case 2:
        n = Math.floor(Math.random() * 100000000);
        return ["Please enter the natural log of", n, "to 5 decimal places", Math.log(n).toFixed(5)];
      case 3: {
        const text = `"${Math.random().toString(36).substring(2, 15)}"`;
        return ["Please enter the SHA-256 hash of", text, "hexadecimal encoded", sha256(text)];
      }
      case 4: {
        const fn = Math.random() < 0.5 ? Math.sin : Math.cos;
        n = Number((Math.random() * 95 + 5).toPrecision(3));
        return ["Please enter the definite integral of", `${fn === Math.sin ? "sin" : "cos"}(x) from 0 to ${n}`,
          "to 3 decimal places", integral(n, fn).toFixed(3)];
      }
      case 5: {
        n = Number((Math.random() * 9.9 + 0.1).toFixed(1));
        let errorNum = 0.1, i = 0;
        while (String(n + errorNum) === String(parseFloat((n + errorNum).toFixed(10)))) {
          if (i > 100) {
            n = Number((Math.random() * 9.9 + 0.1).toFixed(1));
            errorNum = 0.1;
            i = 0;
          }
          errorNum = Number((errorNum + 0.1).toFixed(1));
          i++;
        }
        return ["Please enter the result of", `${n} + ${errorNum}`, "according to the people at IEEE", n + errorNum];
      }
      case 6: {
        const magnitude = Number((Math.random() * 100).toPrecision(3));
        const angle = Number((Math.random() * 90).toPrecision(3));
        return ["Please enter the horizontal component of", `a vector with magnitude ${magnitude} and direction ${angle}°`,
          "to 3 decimal places", (magnitude * Math.cos(angle * (Math.PI / 180))).toFixed(3)];
      }
      case 7:
        n = Number((Math.random() * 99 + 1).toFixed(0));
        return ["Please enter the volume of a", `rhombicosidodecahedron with edge length ${n}`,
          "to 2 decimal places", ((n ** 3 / 3) * (60 + 29 * Math.sqrt(5))).toFixed(2)];
    }
  }

  function showText(top, main, bottom) {
    instruction.textContent = top;
    title.textContent = main;
    format.textContent = bottom;
  }

  function positionPopup() {
    if (!popup.hasAttribute("data-show")) return;
    const rect = opener.getBoundingClientRect();
    const width = popup.offsetWidth, height = popup.offsetHeight;
    let left = rect.right + 16;
    if (left + width > window.innerWidth - 8 && rect.left - 16 - width >= 8) {
      left = rect.left - 16 - width;
    }
    popup.style.left = `${Math.max(8, Math.min(left, window.innerWidth - width - 8))}px`;
    popup.style.top = `${Math.max(8, Math.min(rect.top + rect.height / 2 - height / 2, window.innerHeight - height - 8))}px`;
  }

  function drawTimer(remaining) {
    timerValue.textContent = remaining > 0 ? Math.ceil(remaining) : ":(";
    timerProgress.style.strokeDashoffset = 1 - remaining / duration;
    const mix = Math.max(0, Math.min(1, (duration - remaining) / (duration - 1.5)));
    const start = [26, 115, 232], end = [222, 82, 70];
    timerProgress.style.stroke = `rgb(${start.map((v, i) => Math.round(v + (end[i] - v) * mix)).join(",")})`;
  }

  function tick() {
    if (state !== "playing") return;
    const remaining = Math.max(0, (deadline - performance.now()) / 1000);
    drawTimer(remaining);
    if (remaining === 0) feedback("timeout");
    else frame = requestAnimationFrame(tick);
  }

  function startRound() {
    const challenge = generateChallenge();
    answer = String(challenge[3]);
    showText(...challenge);
    header.className = "popup-header";
    input.value = "";
    input.disabled = submit.disabled = false;
    state = "playing";
    positionPopup();
    input.focus({ preventScroll: true });
    deadline = performance.now() + duration * 1000;
    tick();
  }

  function feedback(result) {
    if (state !== "playing") return;
    state = "feedback";
    cancelAnimationFrame(frame);
    input.value = "";
    input.disabled = submit.disabled = true;
    header.className = result === "correct" ? "popup-header-green" : "popup-header-red";
    if (result === "correct") {
      numCorrect++;
      showText("Hmmm, you might actually be a robot", "correct", `${numCorrect}/${requiredCorrect} complete`);
    } else {
      numCorrect = 0;
      showText(result === "timeout" ? "Hurry up, slowass" : "I dunno, you look pretty human to me",
        "try again", `${numCorrect}/${requiredCorrect} complete`);
    }
    if (numCorrect >= requiredCorrect) {
      state = "complete";
      printFlag();
      wrapper.classList.remove("visible");
      opener.classList.add("hidden");
      opener.setAttribute("aria-expanded", "false");
      document.getElementById("check").classList.remove("hidden");
      document.getElementById("verification-status").textContent = "Verification complete. You're a robot!";
      input.blur();
      setTimeout(() => popup.removeAttribute("data-show"), 200);
      return;
    }
    setTimeout(() => {
      duration = 4 + (duration - 4) * 0.9;
      startRound();
    }, 2000);
  }

  opener.addEventListener("click", () => {
    if (state !== "closed") return;
    popup.setAttribute("data-show", "");
    wrapper.classList.add("visible");
    opener.setAttribute("aria-expanded", "true");
    startRound();
  });
  popup.addEventListener("submit", event => {
    event.preventDefault();
    if (state !== "playing") return;
    if (performance.now() >= deadline) {
      drawTimer(0);
      feedback("timeout");
      return;
    }
    feedback(input.value !== "" && input.value === answer ? "correct" : "wrong");
  });
  window.addEventListener("resize", positionPopup);
})();
