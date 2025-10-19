# 🧠 GameAI-Pathfinder: A Comparative Study on Intelligent Game Agents
> Comparative implementation of **A\*** and **Q-Learning** for adaptive pathfinding in 2D grid environments — bridging classical search and modern reinforcement learning.

![GitHub Repo stars](https://img.shields.io/github/stars/omdeshpande09012005/GameAI-Pathfinder?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/omdeshpande09012005/GameAI-Pathfinder)


## 🎯 Project Overview
**GameAI-Pathfinder** is a research and engineering project built in **C++** that provides a rigorous comparison between two fundamental pathfinding approaches: the **A\*** search algorithm and **Q-Learning** (a model-free reinforcement learning technique). The project is designed to analyze how autonomous agents learn to navigate complex, obstacle-rich, 2D grid environments, bridging the gap between traditional search algorithms and modern machine learning. This project is part of Om Deshpande’s research work in AI and Game Intelligence, emphasizing reproducible experiments, robust data analysis, and publication-ready results.

---

## 🧩 Core Features
| Feature | Description |
| :--- | :--- |
| **A*** **Search** | Heuristic-based pathfinding using **Manhattan distance** for optimal, deterministic solutions. |
| **Q-Learning Agent** | A reinforcement learning agent employing an **ε-greedy policy**, sophisticated reward shaping, and decaying exploration. |
| **Grid Environment** | Modular, loadable maps defined by text files (e.g., maps/demo_map.txt). |
| **Experiment Runner** | Automated benchmarking and metric collection via a **PowerShell script** (experiments/run_all.ps1). |
| **Analysis & Visualization** | Python scripts for data analysis and visualization, comparing performance metrics (experiments/analyze.py). |
| **Research Artifacts** | Includes a full paper draft and figures (paper/AI_in_Games_SlimeEscape.md) for potential publication. |

---

## 🧱 Project Structure
```
GameAI-Pathfinder/
├── src/                # C++ source files (Agent implementations, Grid/Map logic, main)
├── maps/               # Text-based map layouts and environment files
├── experiments/        # Scripts for automation (PowerShell) & data analysis (Python)
├── results/            # Automatically generated data (.csv) and plots (.png)
├── paper/              # Research paper drafts and supporting documents
├── CMakeLists.txt      # CMake build configuration
├── README.md           # Project documentation
└── .gitignore
```

---

## ⚙️ Setup & Execution
### 1. **Local Setup**
Assuming a Windows environment with **PowerShell** and **MinGW/CMake** installed:

```bash
# 1️⃣ Clone the repository
git clone https://github.com/<your-username>/GameAI-Pathfinder.git
cd GameAI-Pathfinder

# 2️⃣ Configure & build the C++ project
mkdir build
cd build
cmake .. -G "MinGW Makefiles"
cmake --build .
cd ..

# 3️⃣ Run a quick test (e.g., A* or Q-Learning on a map)
.\build\slime_escape.exe maps\demo_map.txt
```

### 2. 🧪 Running Automated Experiments
To run multiple iterations and collect comparative metrics, use the automated experiment runner:

```powershell
# Set execution policy to run the local script (if necessary)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Execute the full benchmark script
.\experiments\run_all.ps1
```

This script will:
- Rebuild the project.
- Run 3 iterations each of the A* and Q-Learning agents.
- Save comprehensive metrics to results/metrics.csv.

Example metrics.csv output:
```
algo,map,seed,run,steps,time_ms,success
astar,demo,42,1,20,0,1
qlearn,demo,42,1,20,0,1
```

### 3. 📊 Data Analysis & Visualization
After running the experiments, generate visual comparisons using the Python analysis script:

```bash
# Install required dependencies
pip install pandas matplotlib

# Run the analysis script
python experiments\analyze.py
```

Plots will be generated and saved in the results/plots/ directory:
- path_length_comparison.png
- success_rate.png
- steps_per_run.png

---

## 🧠 Research Context & Findings
This project specifically investigates:
- Comparative algorithmic performance (A* vs. Q-Learning) on path length and computation time.
- The convergence rate of the Q-Learning agent in obstacle-rich environments.
- The scalability and generalization potential of reinforcement-based agents.

The findings are synthesized in the planned research paper, “Comparative Analysis of Heuristic and Reinforcement Learning Agents for Pathfinding in 2D Game Environments,” available as a draft in `/paper/AI_in_Games_SlimeEscape.md`.

### 📈 Sample Results (Preliminary)
| Algorithm | Avg Steps | Success Rate | Remarks |
| :--- | :---: | :---: | :--- |
| A* | 20 | 100% | Deterministic, guaranteed optimal path. |
| Q-Learning | 20 | 100% | Successfully converged to the optimal path after 1000 training episodes. |

---

## 🧰 Tech Stack
| Category | Tools / Libraries |
| :--- | :--- |
| Language | C++17 |
| Build System | CMake + MinGW |
| AI Framework | Custom-built A* and Q-Learning implementations |
| Data Analysis | Python (Pandas, Matplotlib) |
| Automation | PowerShell |
| Version Control | Git + GitHub |

---

## 💡 Future Work
This project serves as a strong foundation, with several planned extensions:
- Deep Q-Learning (DQN): Integrate a neural network-based agent for high-dimensional state spaces.
- Procedural Content: Implement procedural map generation for testing generalization.
- Optimization: Fine-tune reward shaping and hyperparameter search.
- Visualization: Integration with a graphics library (e.g., SFML) for real-time path and learning curve display.

---

## 🧑‍💻 Author
Om Deshpande  
B.Tech CSE @ MIT-WPU Pune  
📚 Research Interest: AI in Games, Systems, and Scalable Learning Architectures  
🎮 Member @ Squad Up Esports | ⚙️ Ex-Intern @ Gtek Computers  

💼 LinkedIn [http://www.linkedin.com/in/omdeshpande09]

💻 GitHub [https://github.com/omdeshpande09012005]

🌐 Portfolio [https://my-portfolio-omdeshpande09012005s-projects.vercel.app/]

---

🧾 License  
MIT License © 2025 Om Deshpande.  
You are free to use, modify, and distribute this project with attribution.

