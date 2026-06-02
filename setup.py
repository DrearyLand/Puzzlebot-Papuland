from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'puzzlebot_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.[yma]*'))),
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', 'FinalChallenge.rviz'))),
        (os.path.join('share', package_name, 'meshes'), glob(os.path.join('meshes', '*.stl'))),
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.urdf'))),
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.xacro'))),
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.world'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jp',
    maintainer_email='jp@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'Minichallenge1 = puzzlebot_sim.Minichallenge1:main',
            'sim_node = puzzlebot_sim.puzzlebot_sim_node:main',
            'loc_node = puzzlebot_sim.localisation_node:main',
            'ctrl_node = puzzlebot_sim.control_node:main',
            'traj_node = puzzlebot_sim.trajectory_node:main',
            'bug0_node = puzzlebot_sim.bug0_node:main',
            'bug2_node = puzzlebot_sim.bug2_node:main',
            'bug0_FC_node = puzzlebot_sim.bug0_FC_node:main',
            'bug2_FC_node = puzzlebot_sim.bug2_FC_node:main',
            'ekf_physical_node = puzzlebot_sim.ekf_physical_node:main',
            'waypoint_manager = puzzlebot_sim.waypoint_manager:main',
            'arucostatus = puzzlebot_sim.arucostatus:main',
            'localisation_node = puzzlebot_sim.localisation_node:main',
        ],
    },
)
