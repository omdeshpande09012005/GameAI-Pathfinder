#include "grid.h"
#include <fstream>
#include <iostream>
#include <cerrno>
#include <cstring>

bool Grid::loadFromFile(const std::string &path){
    std::cout << "[DEBUG] Grid::loadFromFile trying path: \"" << path << "\"" << std::endl;
    std::ifstream in(path);
    if(!in.is_open()){
        std::cerr << "[DEBUG] Failed to open file: \"" << path << "\". errno: " << errno
                  << " (" << std::strerror(errno) << ")" << std::endl;
        return false;
    }
    grid.clear();
    std::string line;
    int y = 0;
    while(std::getline(in, line)){
        grid.push_back(line);
        for(int x=0;x<(int)line.size();++x){
            if(line[x] == 'S'){ startx = x; starty = y; }
            if(line[x] == 'G'){ goalx = x; goaly = y; }
        }
        y++;
    }
    h = grid.size();
    w = (h>0) ? (int)grid[0].size() : 0;
    std::cout << "[DEBUG] Loaded map: width=" << w << " height=" << h
              << " start=(" << startx << "," << starty << ") goal=(" << goalx << "," << goaly << ")" << std::endl;
    return true;
}

std::vector<std::pair<int,int>> Grid::neighbors(int x,int y) const {
    std::vector<std::pair<int,int>> out;
    const int dx[4] = {1,-1,0,0};
    const int dy[4] = {0,0,1,-1};
    for(int i=0;i<4;i++){
        int nx=x+dx[i], ny=y+dy[i];
        if(nx>=0 && nx<w && ny>=0 && ny<h && grid[ny][nx] != '#'){
            out.emplace_back(nx,ny);
        }
    }
    return out;
}

bool Grid::isBlocked(int x,int y) const {
    if(x<0 || x>=w || y<0 || y>=h) return true;
    return grid[y][x] == '#';
}

void Grid::render() const {
    for(auto &line: grid) std::cout << line << "\n";
}
