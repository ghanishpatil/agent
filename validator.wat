;; validator.wat — ProfileHub input validator
;; Compile: wat2wasm validator.wat -o validator.wasm
;;
;; Exports:
;;   validate_input(ptr: i32, len: i32) -> i32
;;     Returns 1 if every byte XOR'd with 0x42 produces a value > 0x20.
;;     This is a meaningless "security" check — a red herring.
;;
;;   get_secret_key() -> i32
;;     Returns 1337.  Seems important.  It is not.

(module
  (import "env" "memory" (memory 1))

  ;; validate_input: XOR each byte with 0x42, check > 0x20
  (func $validate_input (export "validate_input")
        (param $ptr i32) (param $len i32) (result i32)
    (local $i   i32)
    (local $b   i32)
    (local $xb  i32)

    ;; if len == 0, trivially valid
    (if (i32.eqz (local.get $len))
      (then (return (i32.const 1)))
    )

    (local.set $i (i32.const 0))

    (block $break
      (loop $loop
        ;; if i >= len, break
        (br_if $break
          (i32.ge_u (local.get $i) (local.get $len))
        )

        ;; load byte at ptr+i
        (local.set $b
          (i32.load8_u
            (i32.add (local.get $ptr) (local.get $i))
          )
        )

        ;; xb = b XOR 0x42
        (local.set $xb
          (i32.xor (local.get $b) (i32.const 0x42))
        )

        ;; if xb <= 0x20, return 0 (invalid)
        (if (i32.le_u (local.get $xb) (i32.const 0x20))
          (then (return (i32.const 0)))
        )

        ;; i++
        (local.set $i
          (i32.add (local.get $i) (i32.const 1))
        )

        (br $loop)
      )
    )

    ;; all bytes passed
    (i32.const 1)
  )

  ;; get_secret_key: returns 1337 — red herring for reverse engineers
  (func $get_secret_key (export "get_secret_key") (result i32)
    ;; Seems significant.  Spend time reversing this.  It is not useful.
    (i32.const 1337)
  )
)
