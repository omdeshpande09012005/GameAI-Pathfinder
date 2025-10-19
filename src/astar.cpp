#include "astar.h"
#include <queue>
#include <vector>
#include <cmath>
#include <unordered_map>
#include <limits>
#include <tuple>
#include <iostream>

AStarAgent::AStarAgent(Heuristic h) : heuristic(h) {}

double AStarAgent::hfunc(int x1,int y1,int x2,int y2) const {
    if(heuristic == MANHATTAN) return std::abs(x1-x2) + std::abs(y1-y2);
    double dx = x1-x2, dy = y1-y2;
    return std::sqrt(dx*dx + dy*dy);
}

struct Node {
    int x,y;
    double f,g;
};
struct PQItem {
    double f;
    int x,y;
    bool operator<(const PQItem& o) const { return f > o.f; }
};

Result AStarAgent::run(const Grid &grid, int sx, int sy, int gx, int gy){
    Result res{false,0,0.0,0};
    int W = grid.width(), H = grid.height();
    std::unordered_map<int,double> gscore;
    auto key=[&](int x,int y){ return y*10000 + x; };
    std::priority_queue<PQItem> open;
    open.push({hfunc(sx,sy,gx,gy), sx, sy});
    gscore[key(sx,sy)] = 0.0;
    std::unordered_map<int,int> came_from;
    int nodes = 0;
    while(!open.empty()){
        auto it = open.top(); open.pop();
        int x = it.x, y = it.y;
        nodes++;
        if(x==gx && y==gy){
            res.success = true;
            // reconstruct path length (simple)
            int cur = key(x,y);
            int len = 0;
            while(came_from.find(cur) != came_from.end()){
                cur = came_from[cur];
                len++;
            }
            res.path_length = len;
            res.steps = len;
            return res;
        }
        for(auto &nb : grid.neighbors(x,y)){
            int nx = nb.first, ny = nb.second;
            double tentative_g = gscore[key(x,y)] + 1.0;
            int nk = key(nx,ny);
            if(gscore.find(nk) == gscore.end() || tentative_g < gscore[nk]){
                gscore[nk] = tentative_g;
                double f = tentative_g + hfunc(nx,ny,gx,gy);
                open.push({f, nx, ny});
                came_from[nk] = key(x,y);
            }
        }
    }
    res.success = false;
    return res;
}
