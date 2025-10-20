# experiments/run_grid.ps1
# Run a grid of Q-Learning experiments and collect results in results/metrics_all.csv
# Usage: open PowerShell in project root and run:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\experiments\run_grid.ps1

$ErrorActionPreference = "Stop"

# ---------- Config (edit these arrays to change grid) ----------
$trainList  = @(500, 1000, 2000, 5000)    # training episodes to try
$alphaList  = @(0.05, 0.1)                # learning rates
$gammaList  = @(0.9, 0.99)                # discount factors
$epsList    = @(0.3, 0.2)                 # starting epsilon values
$runsPerConfig = 3                        # number of evaluation runs after training (the exe will be called with --runs)
$seed = 42                                # RNG seed used for experiments
# ----------------------------------------------------------------

# Resolve paths
$ProjectRoot = (Get-Location).Path
$BuildDir = Join-Path $ProjectRoot "build"
$Exe = Join-Path $BuildDir "slime_escape.exe"
$Map = Join-Path $ProjectRoot "maps\demo_map.txt"
$ResultsDir = Join-Path $ProjectRoot "results"
New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null

# Output CSV
$OUT = Join-Path $ResultsDir "metrics_all.csv"

# CSV header (columns expected by analysis scripts)
"algo,map,seed,run,train_episodes,alpha,gamma,eps,steps,time_ms,success" | Out-File -Encoding ascii -FilePath $OUT

# Basic checks
if (-not (Test-Path $Exe)) {
    Write-Error "Executable not found at $Exe. Build the project first."
    exit 1
}
if (-not (Test-Path $Map)) {
    Write-Error "Map file not found at $Map"
    exit 1
}

# Show quick summary of planned work
$totalConfigs = $trainList.Count * $alphaList.Count * $gammaList.Count * $epsList.Count
Write-Host "Grid will run $totalConfigs configs x $runsPerConfig eval runs -> approx $($totalConfigs * $runsPerConfig) total evaluation runs."

# Loop the grid
foreach ($te in $trainList) {
    foreach ($a in $alphaList) {
        foreach ($g in $gammaList) {
            foreach ($e in $epsList) {
                Write-Host "== Config: train=$te alpha=$a gamma=$g eps=$e =="
                # Run Q-Learning: the executable trains and then runs evaluation runs (--runs)
                $cmdArgs = @(
                    "--algo", "qlearn",
                    "--map", $Map,
                    "--train-episodes", $te.ToString(),
                    "--seed", $seed.ToString(),
                    "--runs", $runsPerConfig.ToString(),
                    "--alpha", $a.ToString(),
                    "--gamma", $g.ToString(),
                    "--eps", $e.ToString()
                )
                # Execute and capture output lines
                $procOutput = & $Exe $cmdArgs 2>&1

                # Parse Q-Learn lines (one or more "Q-Learn: ..." lines)
                foreach ($line in $procOutput) {
                    $sline = $line.Trim()
                    # match lines like: Q-Learn: success=1 steps=20 path_len=20 time_ms=0.123
                    if ($sline -match '^Q-Learn:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
                        $success = $matches[1]; $steps = $matches[2]; $time = $matches[4]
                        $csv = "qlearn,demo,$seed,1,$te,$a,$g,$e,$steps,$time,$success"
                        $csv | Out-File -FilePath $OUT -Append -Encoding ascii
                    }
                }

                # Optional: baseline A* (single run) for the same map (append to CSV)
                $astarOutput = & $Exe --algo astar --map $Map 2>&1
                foreach ($line in $astarOutput) {
                    $sline = $line.Trim()
                    if ($sline -match '^A\*:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
                        $success = $matches[1]; $steps = $matches[2]; $time = $matches[4]
                        # For A* we still include the hyperparam columns (train_episodes/alpha/gamma/eps) to keep CSV shape
                        $csv = "astar,demo,$seed,1,$te,$a,$g,$e,$steps,$time,$success"
                        $csv | Out-File -FilePath $OUT -Append -Encoding ascii
                    }
                }
            }
        }
    }
}

Write-Host "Grid complete. Results written to: $OUT"
