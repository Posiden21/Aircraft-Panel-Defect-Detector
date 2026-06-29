#include <chrono>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

using namespace std::chrono_literals;

class DefectDetector : public rclcpp::Node {
public:
    DefectDetector() : Node("defect_detector") {
        // Declare parameters for image processing thresholds
        this->declare_parameter("canny_threshold1", 100);
        this->declare_parameter("canny_threshold2", 200);

        subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
            "/camera/image_raw", 10,
            std::bind(&DefectDetector::image_callback, this, std::placeholders::_1));

        publisher_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/annotated_image", 10);
        metadata_pub_ = this->create_publisher<vision_msgs::msg::Detection2DArray>("/detector/metadata", 10);
    }

private:
    void image_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
        try {
            // Convert ROS Image to OpenCV Mat
            cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
            cv::Mat &frame = cv_ptr->image;

            // 1. Perception Logic: Detect Defects
            cv::Mat gray, edges;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            cv::GaussianBlur(gray, gray, cv::Size(5, 5), 0);

            int thresh1 = this->get_parameter("canny_threshold1").as_int();
            int thresh2 = this->get_parameter("canny_threshold2").as_int();
            cv::Canny(gray, edges, thresh1, thresh2);

            std::vector<std::vector<cv::Point>> contours;
            cv::findContours(edges, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

            // 2. Prepare ROS Messages
            vision_msgs::msg::Detection2DArray detection_array;
            detection_array.header = msg->header;

            for (size_t i = 0; i < contours.size(); i++) {
                double area = cv::contourArea(contours[i]);
                if (area > 50.0) { // Filter noise
                    cv::Rect rect = cv::boundingRect(contours[i]);
                    cv::rectangle(frame, rect, cv::Scalar(0, 0, 255), 2); // Draw annotation

                    // Populate Detection2D for JSON metadata emission
                    vision_msgs::msg::Detection2D detection;
                    detection.bbox.center.position.x = rect.x + rect.width / 2.0;
                    detection.bbox.center.position.y = rect.y + rect.height / 2.0;
                    detection.bbox.size_x = rect.width;
                    detection.bbox.size_y = rect.height;
                    detection_array.detections.push_back(detection);
                }
            }

            // Publish annotated image & metadata
            publisher_->publish(*cv_ptr->toImageMsg());
            metadata_pub_->publish(detection_array);

        } catch (cv_bridge::Exception& e) {
            RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
        }
    }

    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr publisher_;
    rclcpp::Publisher<vision_msgs::msg::Detection2DArray>::SharedPtr metadata_pub_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DefectDetector>());
    rclcpp::shutdown();
    return 0;
}
