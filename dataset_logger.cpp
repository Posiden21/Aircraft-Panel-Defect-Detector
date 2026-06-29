#include <fstream>
#include <filesystem>
#include <rclcpp/rclcpp.hpp>
#include <vision_msgs/msg/detection2_d_array.hpp>

class DatasetLogger : public rclcpp::Node {
public:
    DatasetLogger() : Node("dataset_logger") {
        csv_file_.open("defect_dataset.csv", std::ios::out);
        csv_file_ << "timestamp,detection_id,center_x,center_y,width,height\n";

        metadata_sub_ = this->create_subscription<vision_msgs::msg::Detection2DArray>(
            "/detector/metadata", 10,
            std::bind(&DatasetLogger::metadata_callback, this, std::placeholders::_1));
        
        std::filesystem::create_directory("json_records");
    }

    ~DatasetLogger() {
        if (csv_file_.is_open()) csv_file_.close();
    }

private:
    void metadata_callback(const vision_msgs::msg::Detection2DArray::SharedPtr msg) {
        auto timestamp = this->now().seconds();
        
        for (size_t i = 0; i < msg->detections.size(); ++i) {
            const auto& det = msg->detections[i];
            
            // 1. Log to CSV
            csv_file_ << timestamp << "," 
                      << i << ","
                      << det.bbox.center.position.x << ","
                      << det.bbox.center.position.y << ","
                      << det.bbox.size_x << ","
                      << det.bbox.size_y << "\n";

            // 2. Emit JSON Metadata
            std::string json_path = "json_records/frame_" + std::to_string(timestamp) + "_det_" + std::to_string(i) + ".json";
            std::ofstream json_file(json_path);
            json_file << "{\n"
                      << "  \"timestamp\": " << timestamp << ",\n"
                      << "  \"bbox\": {\n"
                      << "    \"center_x\": " << det.bbox.center.position.x << ",\n"
                      << "    \"center_y\": " << det.bbox.center.position.y << ",\n"
                      << "    \"width\": " << det.bbox.size_x << ",\n"
                      << "    \"height\": " << det.bbox.size_y << "\n"
                      << "  }\n"
                      << "}\n";
            json_file.close();
        }
    }

    std::ofstream csv_file_;
    rclcpp::Subscription<vision_msgs::msg::Detection2DArray>::SharedPtr metadata_sub_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DatasetLogger>());
    rclcpp::shutdown();
    return 0;
}
