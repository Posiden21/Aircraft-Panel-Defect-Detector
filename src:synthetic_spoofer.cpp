#include <chrono>
#include <memory>
#include <random>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>

using namespace std::chrono_literals;

class SyntheticSpoofer : public rclcpp::Node {
public:
    SyntheticSpoofer() : Node("synthetic_spoofer"), rng_(std::random_device{}()) {
        // Core publishing setup
        image_pub_ = this->create_publisher<sensor_msgs::msg::Image>("/camera/image_raw", 10);
        timer_ = this->create_wall_timer(500ms, std::bind(&SyntheticSpoofer::timer_callback, this));
        
        RCLCPP_INFO(this->get_logger(), "Synthetic Spoofer Node initialized at 2 Hz.");
    }

private:
    void timer_callback() {
        // 1. Generate a raw aluminum aircraft panel frame (640x480)
        cv::Mat frame(480, 640, CV_8UC3, cv::Scalar(180, 180, 180));

        // Add a subtle metallic texture noise
        cv::Mat noise(frame.size(), frame.type());
        cv::randn(noise, cv::Scalar(0, 0, 0), cv::Scalar(5, 5, 5));
        cv::add(frame, noise, frame);

        // 2. Draw nominal aircraft structural features (Rivets)
        for (int y = 40; y < 480; y += 80) {
            for (int x = 40; x < 640; x += 80) {
                cv::circle(frame, cv::Point(x, y), 8, cv::Scalar(130, 130, 130), -1);
                cv::circle(frame, cv::Point(x, y), 8, cv::Scalar(210, 210, 210), 1);
            }
        }

        // 3. Randomly inject defects to challenge the defect_detector node
        std::uniform_real_distribution<double> die(0.0, 1.0);
        
        if (die(rng_) > 0.4) {
            // High-contrast deep scratch (Linear defect)
            std::uniform_int_distribution<int> coord_x(50, 550);
            std::uniform_int_distribution<int> coord_y(50, 400);
            std::uniform_int_distribution<int> length(30, 100);

            int x1 = coord_x(rng_);
            int y1 = coord_y(rng_);
            int x2 = x1 + length(rng_);
            int y2 = y1 + length(rng_) / 2;

            cv::line(frame, cv::Point(x1, y1), cv::Point(x2, y2), cv::Scalar(40, 40, 40), 2);
        }

        if (die(rng_) > 0.6) {
            // Surface corrosion / pitting defect (Irregular shape contour)
            std::uniform_int_distribution<int> coord_x(100, 500);
            std::uniform_int_distribution<int> coord_y(100, 350);
            
            int cx = coord_x(rng_);
            int cy = coord_y(rng_);
            
            std::vector<cv::Point> pts;
            pts.push_back(cv::Point(cx, cy));
            pts.push_back(cv::Point(cx + 25, cy - 10));
            pts.push_back(cv::Point(cx + 40, cy + 15));
            pts.push_back(cv::Point(cx + 15, cy + 30));
            pts.push_back(cv::Point(cx - 10, cy + 10));

            std::vector<std::vector<cv::Point>> contour_list = {pts};
            cv::drawContours(frame, contour_list, 0, cv::Scalar(70, 90, 80), -1);
        }

        // 4. Convert OpenCV image matrix back to ROS message type
        std::shared_ptr<sensor_msgs::msg::Image> img_msg = 
            cv_bridge::CvImage(std::make_shared<std::logic_error>("Empty header")->set_header(this->get_clock()->now()), 
            "bgr8", frame).toImageMsg();
            
        img_msg->header.frame_id = "camera_frame";
        img_msg->header.stamp = this->get_clock()->now();

        image_pub_->publish(*img_msg);
    }

    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr image_pub_;
    rclcpp::WallTimer::SharedPtr timer_;
    std::mt19932 rng_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SyntheticSpoofer>());
    rclcpp::shutdown();
    return 0;
}
