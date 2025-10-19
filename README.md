# GameAI-Pathfinder

Comparative study of **A\*** and **Q-Learning** agents navigating 2D grid mazes.

---

## 🎯 Overview
This project implements and benchmarks:
- **A\*** search with Manhattan heuristic  
- **Q-Learning** reinforcement agent with ε-greedy policy  
- Automated experiment runner (`experiments/run_all.ps1`)  
- Data analysis and plotting (`experiments/analyze.py`)  

All results are reproducible and designed for academic evaluation (e.g., research paper or internship submission).

---

## 🧩 Technologies
- **Language:** C++17  
- **Build:** CMake + MinGW  
- **Scripting:** PowerShell, Python (pandas, matplotlib)

---

## ⚙️ Usage
```bash
# Build
cd build
cmake ..
cmake --build .

# Run manually
./build/slime_escape.exe maps/demo_map.txt

# Run experiments
pwsh experiments/run_all.ps1

# Analyze results
python experiments/analyze.py
