// src/qlearning.cpp
#include "qlearning.h"
#include <random>
#include <iostream>
#include <limits>
#include <cstdint>
#include <fstream>   // for ofstream/ifstream
#include <sstream>

// cross-platform mkdir
#ifdef _WIN32
  #include <direct.h>
  #define MKDIR(path) _mkdir(path)
#else
  #include <sys/stat.h>
  #include <sys/types.h>
  #define MKDIR(path) mkdir((path), 0755)
#endif

QLearningAgent::QLearningAgent(double a, double g, double e) : alpha(a), gamma(g), eps(e) {}

// pack a state-action into a 64-bit key
int64_t QLearningAgent::stateActionKey(int x,int y,int a) const {
    uint64_t key = 0;
    key |= ( (uint64_t)(uint16_t)y ) << 32;
    key |= ( (uint64_t)(uint16_t)x ) << 16;
    key |= (uint64_t)(uint8_t)a;
    return (int64_t)key;
}

int QLearningAgent::chooseAction(int x,int y,double eps){
    static thread_local std::mt19937 rng(42);
    std::uniform_real_distribution<> ud(0.0,1.0);
    if(ud(rng) < eps) {
        std::uniform_int_distribution<> act(0,3);
        return act(rng);
    }
    double best = -1e18; int besta = 0;
    for(int a=0;a<4;a++){
        int64_t k = stateActionKey(x,y,a);
        double q = 0;
        auto it = qtable.find(k);
        if(it != qtable.end()) q = it->second;
        if(q > best){ best = q; besta = a; }
    }
    return besta;
}

void QLearningAgent::train(const Grid &grid, int gx, int gy, int episodes){
    // ensure results directory exists (cross-platform)
    MKDIR("results"); // if exists, return value non-zero; ignore

    // open CSV log for this training run (overwrites if exists)
    std::ostringstream fn;
    fn << "results/qlearning_train_" << episodes << ".csv";
    std::string outpath = fn.str();
    std::ofstream out(outpath, std::ios::trunc);
    if (out.is_open()) {
        out << "episode,total_reward,epsilon,success\n";
    }

    std::mt19937 rng(123);
    for(int ep=0; ep<episodes; ++ep){
        int x = grid.startX(), y = grid.startY();
        double episode_reward = 0.0;
        bool ep_success = false;
        // store current epsilon for logging (before decay)
        double ep_eps = eps;
        for(int step=0; step<1000; ++step){
            int a = chooseAction(x,y, eps);
            int nx=x, ny=y;
            if(a==0) nx++;
            else if(a==1) nx--;
            else if(a==2) ny++;
            else if(a==3) ny--;
            double reward = -1.0;
            if(grid.isBlocked(nx,ny)){ reward = -50; nx=x; ny=y; }
            if(nx==gx && ny==gy){ reward = 100; ep_success = true; }
            int64_t sak = stateActionKey(x,y,a);
            double maxnext = -1e18;
            for(int a2=0;a2<4;a2++){
                int64_t nk = stateActionKey(nx,ny,a2);
                double qn = 0;
                auto it = qtable.find(nk);
                if(it != qtable.end()) qn = it->second;
                if(qn > maxnext) maxnext = qn;
            }
            if(maxnext < -1e17) maxnext = 0;
            double oldq = 0;
            auto itold = qtable.find(sak);
            if(itold != qtable.end()) oldq = itold->second;
            qtable[sak] = oldq + alpha * (reward + gamma * maxnext - oldq);
            x = nx; y = ny;
            episode_reward += reward;
            if(nx==gx && ny==gy) break;
        }
        // log this episode
        if(out.is_open()){
            out << ep << "," << episode_reward << "," << ep_eps << "," << (ep_success?1:0) << "\n";
        }
        // epsilon decay for next episode
        if(eps > 0.01) eps *= 0.995;
    }

    if(out.is_open()) out.close();
}

Result QLearningAgent::run(const Grid &grid, int sx, int sy, int gx, int gy){
    Result res{false, 0, 0.0, 0};
    int x=sx,y=sy;
    for(int step=0; step<1000; ++step){
        int a = chooseAction(x,y, 0.0); // greedy
        int nx=x, ny=y;
        if(a==0) nx++;
        else if(a==1) nx--;
        else if(a==2) ny++;
        else if(a==3) ny--;
        if(grid.isBlocked(nx,ny)){ nx=x; ny=y; }
        x=nx; y=ny;
        res.steps++;
        if(x==gx && y==gy){
            res.success=true;
            res.path_length = res.steps;     // record path length
            break;
        }
    }
    return res;
}

void QLearningAgent::savePolicy(const std::string &path){
    std::ofstream out(path);
    if(!out.is_open()) return;
    for(auto &p : qtable){
        out << p.first << " " << p.second << "\n";
    }
    out.close();
}

void QLearningAgent::loadPolicy(const std::string &path){
    std::ifstream in(path);
    if(!in.is_open()) return;
    qtable.clear();
    int64_t key; double val;
    while(in >> key >> val){
        qtable[key] = val;
    }
    in.close();
}
