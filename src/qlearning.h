#pragma once
#include "agent.h"
#include <unordered_map>
#include <string>
#include <cstdint>

class QLearningAgent : public Agent {
public:
    QLearningAgent(double alpha=0.1, double gamma=0.99, double eps=0.2);
    Result run(const Grid &grid, int sx, int sy, int gx, int gy) override;
    void train(const Grid &grid, int gx, int gy, int episodes);
    void savePolicy(const std::string &path);
    void loadPolicy(const std::string &path);
private:
    double alpha, gamma, eps;
    std::unordered_map<int64_t,double> qtable;   // 64-bit key to avoid overflow
    int64_t stateActionKey(int x,int y,int a) const;
    int chooseAction(int x,int y,double eps);
};
