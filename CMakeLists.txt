cmake_minimum_required(VERSION 3.15)
project(casino-player LANGUAGES C)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Compilation options
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Create shared library
add_library(casino_player MODULE
        roulette-player.c
)

# Get Python extension suffix directly from sysconfig
execute_process(
        COMMAND ${Python3_EXECUTABLE} -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
        OUTPUT_VARIABLE PYTHON_MODULE_EXTENSION
        OUTPUT_STRIP_TRAILING_WHITESPACE
)

# Set the correct output name
set_target_properties(casino_player PROPERTIES
        PREFIX ""
        OUTPUT_NAME "casino_player"
        SUFFIX "${PYTHON_MODULE_EXTENSION}"
)

# Link with Python
target_include_directories(casino_player PRIVATE
        ${Python3_INCLUDE_DIRS}
)
target_link_libraries(casino_player PRIVATE
        Python3::Python
)

# Create a post-build copy with simpler name
add_custom_command(TARGET casino_player POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
        $<TARGET_FILE:casino_player>
        ${CMAKE_BINARY_DIR}/casino_player.so
)

# Create a symbolic link in source directory
add_custom_command(TARGET casino_player POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E create_symlink
        $<TARGET_FILE:casino_player>
        ${PROJECT_SOURCE_DIR}/casino_player.so
)

# Debug messages
message(STATUS "=== Build Configuration ===")
message(STATUS "Python Version: ${Python3_VERSION}")
message(STATUS "Python Include Dirs: ${Python3_INCLUDE_DIRS}")
message(STATUS "Python Libraries: ${Python3_LIBRARIES}")
message(STATUS "Module Extension: ${PYTHON_MODULE_EXTENSION}")
message(STATUS "Source dir: ${PROJECT_SOURCE_DIR}")
message(STATUS "Binary dir: ${CMAKE_BINARY_DIR}")
message(STATUS "=========================")