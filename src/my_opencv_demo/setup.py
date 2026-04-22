from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'my_opencv_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
        "pub_webcam = my_opencv_demo.pub_webcam:main",
        "sub_image = my_opencv_demo.sub_image:main",
        "senialitas = my_opencv_demo.senialitas:main"
        ],
    },
)
