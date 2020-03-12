#include <iostream>
#include <stdio.h>
#include <string>

#include <pybind11/pybind11.h>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>

#include "Framerate.hpp"

using namespace cv;
using namespace std;

void process(Mat frame, Mat kernel, Scalar low, Scalar high);

Framerate fps;

double run() {
    Mat frame;
    VideoCapture cap;
    Mat kernel = getStructuringElement(MORPH_RECT, Size(10, 10));

    cap.open(0, CAP_V4L);
    if (!cap.isOpened()) {
        cerr << "ERROR: Could not open camera" << endl;
        return -1;
    }

    while (true) {
        cap.read(frame);
        if (frame.empty()) {
            cerr << "ERROR: Blank frame grabbed";
            break;
        }
        process(frame, kernel, Scalar(-10, 50, 50), Scalar(10, 255, 255));

        putText(frame, 
                "FPS: " + to_string(fps.fps),
                Point(10, 30), CV_FONT_HERSHEY_SIMPLEX, 
                1, Scalar(255, 0, 0));

        imshow("Live", frame);
        int key = waitKeyEx(1);
        if (key >= 0) {
            break;
        }

        fps.update();
    }

    destroyAllWindows();
    return fps.fps;
}

void process(Mat frame, Mat kernel, Scalar low, Scalar high) {
    Mat hsv;
    Mat processed;
    vector<vector<Point>> contours;

    cvtColor(frame, hsv, COLOR_BGR2HSV);
    inRange(hsv, low, high, processed);

    morphologyEx(processed, processed, MORPH_OPEN, kernel, Point(-1, -1), 2);
    morphologyEx(processed, processed, MORPH_CLOSE, kernel, Point(-1, -1), 2);

    findContours(processed, contours, RETR_LIST, CHAIN_APPROX_SIMPLE);

    if (contours.size() > 0) {
        vector<Moments> all_moments;
        double max_area = 0;
        vector<Moments>::iterator mc;

        for (auto contour : contours) {
            all_moments.push_back(moments(contour));
            if (all_moments.back().m00 > max_area) {
                max_area = all_moments.back().m00;
                mc = all_moments.end() - 1;
            }
        }

        Point max_contour_centre(mc->m10 / mc->m00, mc->m01 / mc->m00);

        drawMarker(frame, max_contour_centre, Scalar(255, 0, 0));

        drawContours(frame, contours, -1, Scalar(0, 255, 0));

    }
}

PYBIND11_MODULE(video_pipeline, m) {
    m.doc() = "Test video pipeline in C++";

    m.def("run", &run, "Run the pipeline, showing the output with OpenCV highgui");
}
