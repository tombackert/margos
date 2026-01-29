add_library(my_ipc_controller SHARED
   my_ipc_controller.cpp)

# Find ARGoS libraries directly
find_library(ARGOS_CORE_LIB argos3core_simulator PATHS /usr/local/lib/argos3 REQUIRED)
find_library(ARGOS_GENERICROBOT_LIB argos3plugin_simulator_genericrobot PATHS /usr/local/lib/argos3 REQUIRED)
find_library(ARGOS_FOOTBOT_LIB argos3plugin_simulator_footbot PATHS /usr/local/lib/argos3 REQUIRED)

target_link_libraries(my_ipc_controller PUBLIC
   ${ARGOS_CORE_LIB}
   ${ARGOS_GENERICROBOT_LIB}
   ${ARGOS_FOOTBOT_LIB}
   cppzmq
)

target_include_directories(my_ipc_controller PUBLIC
   ${ARGOS_INCLUDE_DIRS}
   "${CMAKE_SOURCE_DIR}/common")
