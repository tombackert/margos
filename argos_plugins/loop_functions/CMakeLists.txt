add_library(zoo_loop_functions SHARED
   zoo_loop_functions.cpp)

# Find ARGoS libraries directly
find_library(ARGOS_CORE_LIB argos3core_simulator PATHS /usr/local/lib/argos3 REQUIRED)
find_library(ARGOS_GENERICROBOT_LIB argos3plugin_simulator_genericrobot PATHS /usr/local/lib/argos3 REQUIRED)

target_link_libraries(zoo_loop_functions PUBLIC
   my_ipc_controller
   ${ARGOS_CORE_LIB}
   ${ARGOS_GENERICROBOT_LIB}
   cppzmq
)

target_include_directories(zoo_loop_functions PUBLIC
   ${ARGOS_INCLUDE_DIRS}
   "${CMAKE_SOURCE_DIR}/common"
   "${CMAKE_SOURCE_DIR}/controllers"
)
