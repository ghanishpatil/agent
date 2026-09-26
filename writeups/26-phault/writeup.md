# PHault (PwnSec CTF 2026) — web, easy, 137 pts

Flag format: `pwnsec{...}`. UNSOLVED live (instances showed a non-responsive DB from my vantage;
event ended), but fully reversed. Class: **time-based blind SQLi where sub-2s timing is masked by a
fixed response-time pad → beat the pad with SLEEP(n) where n > pad.**

## The app (source shown via highlight_file)
```php
$START=microtime(true); ob_start();
register_shutdown_function(function() use($START){
  $remaining = 2.0 - (microtime(true)-$START);
  if ($remaining>0) usleep((int)($remaining*1000000));   // pad EVERY response UP to 2.0s
}); // "no timing attack!!"
mysqli_report(MYSQLI_REPORT_OFF);
$db = new mysqli("127.0.0.1","user","user","chall");
echo highlight_file(__FILE__,true);
if (isset($_GET["id"])) {
  $sql = "SELECT username FROM users WHERE id = ".$_GET["id"];  // raw numeric concat = SQLi
  $res = $db->query($sql);
  if (!$res) die("ill try to tell him, dw");                    // error path
  $row = $res->fetch_row();
  echo 'ill try to tell him, dw';                               // success path (identical text)
}
```

## Why it looks oracle-less (the trap)
- Result is never echoed; die() and echo print the SAME string; syntactically-broken and valid queries
  produced byte-identical bodies → **no boolean/error/UNION-in-body oracle.**
- `register_shutdown_function` pads every response to a **2.0s floor** → **sub-2s timing is dead**
  (the "no timing attack!!" taunt only kills timing UNDER 2s).

## Intended exploit
Time-based blind, but the SLEEP must exceed the pad: `SLEEP(n)` with **n > 2** makes server time = n,
`remaining = 2.0 - n < 0` → no pad → total ≈ n. Each request leaks one bit (condition true ⇒ sleep).
Then binary-search each flag char out of the DB, e.g.:
```
1 AND IF( ASCII(SUBSTRING((SELECT ...flag...),k,1)) > mid, SLEEP(3), 0)
```
CALIBRATION IS MANDATORY (this is where I stalled): a WHERE-clause SLEEP only runs if rows are scanned.
- `1 OR SLEEP(3)` short-circuits on the matching row (no sleep).
- If `users` has 0 rows, a WHERE-clause SLEEP never evaluates.
So calibrate the SLEEP FORM against a KNOWN true/false pair and pick one that fires regardless of rows
(e.g. force evaluation on every scanned row with a non-matching id: `-1 OR SLEEP(3)`, or a
`UNION SELECT SLEEP(3)`), and verify baseline-vs-sleep delta BEFORE extracting.

## My mistakes (recorded in MISTAKES_AND_LESSONS.md)
- Overthought in chat instead of shipping the extractor immediately.
- When SLEEP showed no delay on the given instances, I slid to "DB broken / unsolvable" (forbidden A1/A4)
  instead of treating it as "my SLEEP payload/context is wrong" and pivoting the payload shape, and
  instead of building the calibrated extractor to prove the channel.

## Generalization / TELL
- PHP challenge that prints its own source, result not echoed, die()==echo, and a shutdown-time
  response pad = **time-based blind SQLi with SLEEP > pad**. Build a calibrated boolean-timing extractor
  at minute 1; never conclude "no oracle / broken DB."
