# experiments/run_grid.ps1
# Runs a high-N grid of Q-Learning experiments on a single map for robust data.

$ErrorActionPreference = "Stop"

# ---------- Config (High-N, Single Map) ----------
$trainList 	= @(500, 1000, 2000, 5000) 	 # training episodes to try
$alphaList 	= @(0.05, 0.1) 			 # learning rates
$gammaList 	= @(0.9, 0.99) 			 # discount factors
$epsList 	= @(0.3, 0.2) 			 # starting epsilon values
$runsPerConfig = 20 	 			 # HIGH N for robust stats
$seed = 42 	 				 # RNG seed used for experiments
# ----------------------------------------------------------------

# Resolve paths
$ProjectRoot = (Get-Location).Path
$BuildDir = Join-Path $ProjectRoot "build"
$Exe = Join-Path $BuildDir "slime_escape.exe"
$Map = Join-Path $ProjectRoot "maps\demo_map.txt" # Single map only
$ResultsDir = Join-Path $ProjectRoot "results"
New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null

# Basic checks
if (-not (Test-Path $Exe)) {
    Write-Error "Executable not found at $Exe. Build the project first."
    exit 1
}
if (-not (Test-Path $Map)) {
    Write-Error "Map file not found at $Map"
    exit 1
}

# Output CSV
$OUT = Join-Path $ResultsDir "metrics_all.csv"
# Clear old CSV and write header
"algo,map,seed,run,train_episodes,alpha,gamma,eps,steps,time_ms,success" | Out-File -Encoding ascii -FilePath $OUT

# Show quick summary of planned work
$totalConfigs = $trainList.Count * $alphaList.Count * $gammaList.Count * $epsList.Count
Write-Host "Grid will run $totalConfigs configs x $runsPerConfig eval runs on SINGLE MAP -> approx $($totalConfigs * $runsPerConfig) total evaluation runs."

# Loop the grid
foreach ($te in $trainList) {
    foreach ($a in $alphaList) {
        foreach ($g in $gammaList) {
            foreach ($e in $epsList) {
                Write-Host "== Config: train=$te alpha=$a gamma=$g eps=$e =="

                # Run Q-Learning (Training and Evaluation on the single map)
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

                $procOutput = & $Exe $cmdArgs 2>&1

                # Parse Q-Learn lines (N=20 lines expected)
                $runId = 1
                foreach ($line in $procOutput) {
                    $sline = $line.Trim()
                    if ($sline -match '^Q-Learn:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
                        $success = $matches[1]; $steps = $matches[2]; $time = $matches[4]
                        $csv = "qlearn,demo_map,$seed,$runId,$te,$a,$g,$e,$steps,$time,$success"
                        $csv | Out-File -FilePath $OUT -Append -Encoding ascii
                        $runId++ 
                    }
                }

                # Baseline A* (run N times)
                for ($i = 1; $i -le $runsPerConfig; $i++) {
                    $astarOutput = & $Exe --algo astar --map $Map 2>&1
                    foreach ($line in $astarOutput) {
                        $sline = $line.Trim()
                        if ($sline -match '^A\*:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
                            $success = $matches[1]; $steps = $matches[2]; $time = $matches[4]
                            $csv = "astar,demo_map,$seed,$i,$te,$a,$g,$e,$steps,$time,$success"
                            $csv | Out-File -FilePath $OUT -Append -Encoding ascii
                        }
                    }
                }
            }
        }
    }
}

Write-Host "Grid complete. Results written to: $OUT"