from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'basics_comm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*launch.[pxy][yam]*')),
        (os.path.join('share', package_name), glob('launch/*.[pxy][yam]*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jp',
    maintainer_email='jp@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        'node_python = basics_comm.node_python:main',
        'node_python_OOP = basics_comm.node_python_OOP:main',
        'my_talker = basics_comm.my_talker:main',
        'my_listener = basics_comm.my_listener:main',
        'signal_generator = basics_comm.signal_generator:main',
        'process = basics_comm.process:main',
        'generator = basics_comm.generator:main',
        'counter = basics_comm.counter:main',
        'my_talker_arg = basics_comm.my_talker_arg:main',
        'my_listener_arg = basics_comm.my_listener_arg:main',
        'my_talker_param = basics_comm.my_talker_param:main',
        'my_listener_param = basics_comm.my_listener_param:main',
        'hw_status_publisher = basics_comm.hw_status_publisher:main',
        'read_param = basics_comm.read_param:main',
        ],
    },
)
