# Add this alongside your other executable targets inside CMakeLists.txt

# --- 4. Target: synthetic_spoofer ---
add_executable(synthetic_spoofer src/synthetic_spoofer.cpp)
ament_target_dependencies(synthetic_spoofer
  rclcpp
  sensor_msgs
  cv_bridge
)
target_link_libraries(synthetic_spoofer PRIVATE ${OpenCV_LIBS})

# Update your existing install target rule block to include synthetic_spoofer
install(TARGETS
  defect_detector
  dataset_logger
  synthetic_spoofer
  DESTINATION lib/${PROJECT_NAME}
)
