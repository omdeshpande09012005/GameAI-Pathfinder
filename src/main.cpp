#include <iostream>
#include "grid.h"
#include "astar.h"
#include "qlearning.h"
#include <chrono>

int main(int argc, char** argv){
    std::string mapfile = "maps/demo_map.txt";
    if(argc > 1) mapfile = argv[1];

    Grid grid;
    if(!grid.loadFromFile(mapfile)){
        std::cerr << "Failed to load map: " << mapfile << std::endl;
        return 1;
    }
    grid.render();

    // Example A* run
    AStarAgent astar(AStarAgent::MANHATTAN);
    auto t0 = std::chrono::high_resolution_clock::now();
    Result r = astar.run(grid, grid.startX(), grid.startY(), grid.goalX(), grid.goalY());
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    std::cout << "A*: success="<< r.success << " steps="<< r.steps << " path_len="<< r.path_length << " time_ms="<< ms << std::endl;

    // Example Q-Learning (train a bit)
    QLearningAgent ql(0.1, 0.99, 0.2);
    ql.train(grid, grid.goalX(), grid.goalY(), 500); // episodes
    Result qres = ql.run(grid, grid.startX(), grid.startY(), grid.goalX(), grid.goalY());
    std::cout << "Q-Learn: success="<< qres.success << " steps="<< qres.steps << " path_len="<< qres.path_length << std::endl;

    return 0;
}
