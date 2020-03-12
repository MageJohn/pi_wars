#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>

using namespace cv;
using namespace std;

void process(Mat frame, Mat kernel, Scalar low, Scalar high);

int main() {
    Mat frame;
    VideoCapture cap;
    Mat kernel = getStructuringElement(MORPH_RECT, Size(10, 10));

    cap.open(0, CAP_V4L);
    if (!cap.isOpened()) {
        cerr << "ERROR: Could not open camera" << endl;
        return -1;
    }

    cap.read(frame);
    if (frame.empty()) {
        cerr << "ERROR: Blank frame grabbed";
        break;
    }
    process(frame, kernel, Scalar(-10, 50, 50), Scalar(10, 255, 255));

    vector<int> compression_params;

    bool result = false;
    try {
        result = imwrite("testout.jpg", frame, compression_params);
    } catch (const cv::Exception& ex) {
        cerr << "Exception converting image to JPG";
    }
    if (result) {
        cout << "Saved cap to testout.jpg";
    } else {
        cout << "Couldn't save to testout.jpg";
    }
}
