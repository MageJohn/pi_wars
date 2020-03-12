cmake_minimum_required(VERSION 2.8.12)
project(video_pipeline)

add_subdirectory(pybind11)

find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

pybind11_add_module(video_pipeline VideoPipeline.cpp Framerate.cpp)
target_link_libraries(video_pipeline PRIVATE ${OpenCV_LIBS})

add_executable(standalone_test StandaloneTest.cpp VideoPipeline.cpp Framerate.cpp)

target_link_libraries(standalone_test PRIVATE ${OpenCV_LIBS})
