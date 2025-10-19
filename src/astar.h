#pragma once
#include "agent.h"
#include <tuple>

class AStarAgent : public Agent {
public:
    enum Heuristic { MANHATTAN=0, EUCLIDEAN=1 };
    AStarAgent(Heuristic h = MANHATTAN);
    Result run(const Grid &grid, int sx, int sy, int gx, int gy) override;
private:
    Heuristic heuristic;
    double hfunc(int x1,int y1,int x2,int y2) const;
};
