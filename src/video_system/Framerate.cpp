#include "Framerate.hpp"

using namespace std::chrono;

Framerate::Framerate() {
    insert_point = frametimes.begin();
    last_frame_end = steady_clock::now();
}

void Framerate::update() {
    *insert_point = duration_cast<duration<double>>(
                steady_clock::now() - last_frame_end).count();
    
    last_frame_end = steady_clock::now();

    insert_point ++;
    if (insert_point == frametimes.end()) {
        insert_point = frametimes.begin();
    }

    double sum = 0;
    for (auto time : frametimes) {
        sum += time;
    }
    fps = 1.0/(sum / frametimes.size());
}

