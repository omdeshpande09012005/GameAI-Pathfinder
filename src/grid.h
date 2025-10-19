#pragma once
#include <vector>
#include <string>

struct Result {
    bool success;
    int steps;
    double time_ms;
    int path_length;
};

class Grid {
public:
    Grid() : w(0), h(0), startx(-1), starty(-1), goalx(-1), goaly(-1) {}
    bool loadFromFile(const std::string &path);
    std::vector<std::pair<int,int>> neighbors(int x,int y) const;
    bool isBlocked(int x,int y) const;
    void render() const;
    int width() const { return w; }
    int height() const { return h; }
    int startX() const { return startx; }
    int startY() const { return starty; }
    int goalX() const { return goalx; }
    int goalY() const { return goaly; }
private:
    int w,h;
    int startx,starty,goalx,goaly;
    std::vector<std::string> grid;
};
