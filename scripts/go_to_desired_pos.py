#! /usr/bin/env python3

# import ros stuff
import rospy
from sensor_msgs.msg import LaserScan
from move_base_msgs.msg import MoveBaseActionGoal

from actionlib_msgs.msg import GoalID 

from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *
import time
import math




class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	ORANGE = '\033[33m' 
	PURPLE  = '\033[35m'

msg = """ 
""" + bcolors.BOLD + """
This node makes the robot autonomously reach a x,y position inserted by the user.
The user x,y inputs are published on the 'move_base/goal' topic, and 
therefore the robot is going to plan the path through the Dijkstra's algorithm. 
""" +bcolors.ENDC + """
"""

goal_msg=MoveBaseActionGoal()
goal_cancel=GoalID()
position_=Point()
my_timer = 0
goal_msg.goal.target_pose.header.frame_id = 'map'
goal_msg.goal.target_pose.pose.orientation.w = 1
active_ = rospy.get_param('active')
desired_position_x = rospy.get_param('des_pos_x')
desired_position_y = rospy.get_param('des_pos_y')

def set_goal(x, y):
	goal_msg.goal.target_pose.pose.position.x = x
	goal_msg.goal.target_pose.pose.position.y = y
	pub_goal.publish(goal_msg)

def clbk_odom(msg):

	global position_
	position_ = msg.pose.pose.position

def update_variables():
	global desired_position_x, desired_position_y, active_
	active_ = rospy.get_param('active')
	desired_position_x = rospy.get_param('des_pos_x')
	desired_position_y = rospy.get_param('des_pos_y')

def my_callback_timeout(event):
	if active_==1:
		print (bcolors.FAIL + "Timer called after " + str(event.current_real) + "seconds." + bcolors.ENDC)
		print(bcolors.FAIL + bcolors.BOLD + "Position not reached, target canceled\n" + bcolors.ENDC)
		rospy.set_param('active', 0)

def main():

	global pub_vel 
	global pub_goal

	flag=0
	
	rospy.init_node('go_to_desired_pos')
	pub_goal = rospy.Publisher('/move_base/goal', MoveBaseActionGoal, queue_size=1)
	pub_cancel_goal = rospy.Publisher('/move_base/cancel', GoalID, queue_size=1)
	pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

	pub_goal.publish(goal_msg)
	sub_odom = rospy.Subscriber('/odom', Odometry, clbk_odom)
	rate = rospy.Rate(10)
	print(msg)
	while (1):
		
		update_variables()

		if active_==1:
			
			if flag == 1:
				print(bcolors.OKGREEN + bcolors.UNDERLINE + "The robot is moving towards your desired target" + bcolors.ENDC)
				rospy.Timer(rospy.Duration(120),my_callback_timeout)
				set_goal(desired_position_x, desired_position_y)
				flag = 0

			if abs(desired_position_x-position_.x) <= 0.4 and abs(desired_position_y-position_.y) <= 0.4:
				print(bcolors.OKGREEN + bcolors.UNDERLINE + bcolors.BOLD + "Target reached\n" + bcolors.ENDC)
				rospy.set_param('active', 0)

		else:
			if flag == 0:
				print(bcolors.OKBLUE + "Modality 1 is currently in idle state\n" + bcolors.ENDC)
				pub_cancel_goal.publish(goal_cancel)
				flag = 1

		rate.sleep()


if __name__ == '__main__':
    main()




	

