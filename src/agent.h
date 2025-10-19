#pragma once
#include "grid.h"

class Agent {
public:
    virtual Result run(const Grid &grid, int sx, int sy, int gx, int gy) = 0;
    virtual ~Agent() = default;
};
