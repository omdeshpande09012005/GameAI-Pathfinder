# experiments/run_all_param.ps1
$ErrorActionPreference = "Stop"
$ProjectRoot = (Get-Location).Path
$BuildDir = (Get-Item (Join-Path $ProjectRoot "build")).FullName
$Exe = Join-Path $BuildDir "slime_escape.exe"
$Map = Join-Path $ProjectRoot "maps\demo_map.txt"
$Seed = 42
$ResultsDir = Join-Path $ProjectRoot "results"
New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
$OUT = Join-Path $ResultsDir "metrics_all.csv"
"algo,map,seed,run,train_episodes,steps,time_ms,success" | Out-File -Encoding ascii -FilePath $OUT

# Train sizes to test (you can change)
$trainList = @(500,1000,2000,5000)

foreach ($te in $trainList) {
    Write-Host "== Running Q-Learn (train episodes = $te) =="
    # run executable — it will train then perform 3 evaluation runs (we pass --runs 3)
    $cmdOutput = & $Exe --algo qlearn --train-episodes $te --map $Map --seed $Seed --runs 3 2>&1
    foreach ($line in $cmdOutput) {
        $sline = $line.Trim()
        if ($sline -match '^Q-Learn:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
            $success = $matches[1]; $steps = $matches[2]; $time = $matches[4];
            $csv = "qlearn,demo,$Seed,1,$te,$steps,$time,$success"
            $csv | Out-File -FilePath $OUT -Append -Encoding ascii
        }
    }
    # optional: run A* for baseline once per train size (will append)
    $astarOut = & $Exe --algo astar --map $Map 2>&1
    foreach ($line in $astarOut) {
        $sline = $line.Trim()
        if ($sline -match '^A\*:\s*success=(\d+)\s+steps=(\d+)\s+path_len=(\d+)\s+time_ms=([0-9.]+)') {
            $success = $matches[1]; $steps = $matches[2]; $time = $matches[4]
            $csv = "astar,demo,$Seed,1,$te,$steps,$time,$success"
            $csv | Out-File -FilePath $OUT -Append -Encoding ascii
        }
    }
}

Write-Host "All experiments finished. CSV: $OUT"
