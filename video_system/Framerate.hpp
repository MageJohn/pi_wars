#include <array>
#include <chrono>

class Framerate {
    std::array<double,20> frametimes;

    std::array<double,20>::iterator insert_point;

    std::chrono::steady_clock::time_point last_frame_end;

    public:

    double fps;

    Framerate();

    void update();
};


