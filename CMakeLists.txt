cmake_minimum_required(VERSION 3.10)
project(GameAI_Pathfinder VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler options
if(MSVC)
  add_compile_options(/O2 /W3 /EHsc)
else()
  add_compile_options(-O2 -Wall -Wextra)
endif()

# sources
file(GLOB SRC_FILES src/*.cpp)

add_executable(slime_escape ${SRC_FILES})

# Provide a default build type if not provided
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()
