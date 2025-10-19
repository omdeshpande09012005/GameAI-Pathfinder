# experiments\run_all.ps1
# Robust PowerShell experiment runner for GameAI-Pathfinder
# Run from project root: .\experiments\run_all.ps1

$ErrorActionPreference = "Stop"

# Resolve script/project/build paths as strings (use Get-Item to get FullName)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = (Get-Item (Join-Path $ScriptDir "..")).FullName
$BuildDir = (Get-Item (Join-Path $ProjectRoot "build")).FullName

$ResultsDir = Join-Path $ProjectRoot "results"
$OUT = Join-Path $ResultsDir "metrics.csv"
$Map = Join-Path $ProjectRoot "maps\demo_map.txt"
$Seed = 42

# Ensure results dir exists
if (-not (Test-Path $ResultsDir)) { New-Item -ItemType Directory -Path $ResultsDir | Out-Null }

# CSV header (overwrite previous file)
"algo,map,seed,run,steps,time_ms,success" | Out-File -Encoding ascii -FilePath $OUT

# Build step
Write-Host "Building project in $BuildDir..."
Push-Location $BuildDir
cmake .. 
cmake --build . 
Pop-Location

# Locate executable (check common places)
$ExeCandidates = @(
    (Join-Path $BuildDir "slime_escape.exe"),
    (Join-Path $BuildDir "Release\slime_escape.exe"),
    (Join-Path $BuildDir "Debug\slime_escape.exe")
)
$Exe = $ExeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Exe) { Write-Error "Executable not found under build/. Build failed?"; exit 1 }
Write-Host "Using executable: $Exe"

# run experiments
$algos = @("astar","qlearn")
forEach ($algo in $algos) {
    for ($run=1; $run -le 3; $run++) {
        Write-Host "Running $algo (run $run)..."
        $output = & $Exe $Map 2>&1
        if ($null -eq $output) { $output = @() }
        foreach ($line in $output) {
            $sline = $line.Trim()
            if ($sline -match '^A\*:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
                $success = $matches[1]; $steps = $matches[2]; $time_ms = $matches[4]
                $csvLine = "astar,demo,$Seed,$run,$steps,$time_ms,$success"
                $csvLine | Out-File -Encoding ascii -FilePath $OUT -Append
            } elseif ($sline -match '^Q-Learn:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)') {
                $success = $matches[1]; $steps = $matches[2]; $path_len = $matches[3]
                # Q-Learn currently does not print time_ms; use 0
                $csvLine = "qlearn,demo,$Seed,$run,$steps,0,$success"
                $csvLine | Out-File -Encoding ascii -FilePath $OUT -Append
            }
        }
    }
}

Write-Host "✅ Experiments complete. CSV: $OUT"
