cmake_minimum_required(VERSION 3.8.0)
project(MARLPlatformPlugins)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)
endif()

# Find ARGoS
find_package(ARGoS REQUIRED)

# Find ZeroMQ
find_package(cppzmq REQUIRED)

# Include directories
include_directories(${ARGOS_INCLUDE_DIRS} "${CMAKE_SOURCE_DIR}/common")

# Add subdirectories
add_subdirectory(controllers)
add_subdirectory(loop_functions)
