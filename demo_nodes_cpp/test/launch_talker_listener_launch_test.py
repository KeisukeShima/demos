# Copyright 2019 Apex.AI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import unittest

import launch
import launch_ros
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
import std_msgs.msg
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource


@pytest.mark.launch_test
def generate_test_description():
    talker_listener_launch_file = os.path.join(
        get_package_share_directory('demo_nodes_cpp'),
        'launch',
        'topics',
        'talker_listener.launch.xml',
    )

    talker_listener_node = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(talker_listener_launch_file),
    )

    return (
        launch.LaunchDescription([
            talker_listener_node,
            # Start tests right away - no need to wait for anything
            launch_testing.actions.ReadyToTest(),
        ]),
        {
            'talker_listener': talker_listener_node,
        }
    )


class TestTalkerListenerLink(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the ROS context for the test node
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        # Shutdown the ROS context
        rclpy.shutdown()

    def setUp(self):
        # Create a ROS node for tests
        self.node = rclpy.create_node('test_talker_listener_link')

    def tearDown(self):
        self.node.destroy_node()

    def test_talker_transmits(self, talker_listener, proc_output):
        # Expect the talker to publish strings on '/chatter' and also write to stdout
        msgs_rx = []

        sub = self.node.create_subscription(
            std_msgs.msg.String,
            'chatter',
            lambda msg: msgs_rx.append(msg),
            10
        )
        try:
            # Wait until the talker transmits two messages over the ROS topic
            end_time = time.time() + 10
            while time.time() < end_time:
                rclpy.spin_once(self.node, timeout_sec=0.1)
                if len(msgs_rx) > 2:
                    break

            self.assertGreater(len(msgs_rx), 2)

            # Make sure the talker also output the same data via stdout
            # for msg in msgs_rx:
            #     proc_output.assertWaitFor(
            #         expected_output=msg.data, process=talker_listener
            #     )
        finally:
            self.node.destroy_subscription(sub)


@launch_testing.post_shutdown_test()
class TestExecutablesTutorialAfterShutdown(unittest.TestCase):

    def test_last_process_exit_code(self, proc_info):
        """Test last process exit code."""
        launch_testing.asserts.assertExitCodes(
            proc_info,
        )
