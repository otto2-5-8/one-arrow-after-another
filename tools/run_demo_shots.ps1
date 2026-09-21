# 启动 demo_shots.py 剧本，并在固定时刻截图，输出到 screenshots/
param([string]$Root = (Split-Path -Parent $PSScriptRoot))

$out = Join-Path $Root 'screenshots'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$marker = Join-Path $env:TEMP 'dsh_demo_ready.txt'
Remove-Item $marker -ErrorAction SilentlyContinue

$env:DEMO_MARKER = $marker
$proc = Start-Process -FilePath 'D:\python-3\pythonw.exe' `
    -ArgumentList (Join-Path $Root 'tools\demo_shots.py') -PassThru
Write-Host "demo pid=$($proc.Id)"

$deadline = (Get-Date).AddSeconds(60)
while (-not (Test-Path $marker)) {
    if ((Get-Date) -gt $deadline) { Write-Host 'wait window timeout'; exit 1 }
    Start-Sleep -Milliseconds 100
}

$plan = @(
    @{ t = 2.5;  name = '01_menu.png' },
    @{ t = 4.5;  name = '02_level1.png' },
    @{ t = 7.0;  name = '03_flying.png' },
    @{ t = 9.5;  name = '04_blocked.png' },
    @{ t = 15.5; name = '05_level5_hint.png' },
    @{ t = 23.0; name = '06_win.png' },
    @{ t = 29.0; name = '07_lose.png' }
)

$watch = [Diagnostics.Stopwatch]::StartNew()
foreach ($item in $plan) {
    while ($watch.Elapsed.TotalSeconds -lt $item.t) { Start-Sleep -Milliseconds 50 }
    $target = Join-Path $out $item.name
    powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $Root 'tools\capture_window.ps1') `
        -ProcessId $proc.Id -Out $target | Write-Host
}

if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
Get-ChildItem $out -Filter *.png | Select-Object Name, Length | Format-Table -AutoSize | Out-String
