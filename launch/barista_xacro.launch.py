import os
import random
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix

# this is the function launch  system will look for
def generate_launch_description():

    ####### DATA INPUT ##########
    xacro_file = "barista_robot_model.urdf.xacro"
    package_description = "barista_robot_description"
    # Position [X, Y, Z] and orientation [Roll, Pitch, Yaw]
    position = [0.0, 0.0, 0.2] 
    orientation = [0.0, 0.0, 0.0]
    # Base name for robot
    robot_base_name = "barista_robot"
    # Gazebo ROS package
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_bot_gazebo = get_package_share_directory('barista_robot_description')
    # Name of world to load
    world_name = 'base.world'

    ####### DATA INPUT END ##########

    # Gazebo models
    description_package_name = package_description
    install_dir = get_package_prefix(description_package_name)

    gazebo_models_path = os.path.join(pkg_bot_gazebo, 'meshes')

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    print("Fetching XACRO ==>")

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )   

    # Xacro setup
    xacro_file = os.path.join(pkg_bot_gazebo, 'xacro', xacro_file)
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[params],
        output="screen"
    )

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'config.rviz')

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])

    # Spawn ROBOT Set Gazebo
    entity_name = robot_base_name+"-"+str(int(random.random()*100000))

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=['-entity',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]
                                                     ), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]
                                                        ), '-Y', str(orientation[2]),
                   '-topic', '/robot_description'
                   ]
    )

    # Create and return launch description object
    return LaunchDescription(
        [   DeclareLaunchArgument('world', default_value=[os.path.join(pkg_bot_gazebo, 'worlds', world_name), ''], description='SDF world file'),
            gazebo,
            robot_state_publisher_node,
            rviz_node,
            spawn_robot
        ]
    )