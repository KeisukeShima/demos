// Copyright 2016 Open Source Robotics Foundation, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "composition/talker_component.hpp"

#include <chrono>
#include <iostream>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

namespace composition
{

Talker::Talker()
: Node("talker"), count_(0)
{
  pub_ = create_publisher<std_msgs::msg::String>("chatter");
  timer_ = create_wall_timer(1s, std::bind(&Talker::on_timer, this));
}

void Talker::on_timer()
{
  auto msg = std::make_shared<std_msgs::msg::String>();
  msg->data = "Hello World: " + std::to_string(++count_);
  printf("Publishing: '%s'\n", msg->data.c_str());
  std::flush(std::cout);
  pub_->publish(msg);
}

}  // namespace composition

#include "class_loader/class_loader_register_macro.h"

CLASS_LOADER_REGISTER_CLASS(composition::Talker, rclcpp::Node)
