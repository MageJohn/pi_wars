#include <pybind11/pybind11.h>

extern double run();

PYBIND11_MODULE(video_pipeline, m) {
    m.doc() = "Test video pipeline in C++";

    m.def("run", &run, "Run the pipeline, showing the output with OpenCV highgui");
}
