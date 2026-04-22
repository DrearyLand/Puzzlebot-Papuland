from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'courseworks'

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
    maintainer='andrea',
    maintainer_email='andrea@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        "signal_generator = courseworks.signal_generator:main",
        "process = courseworks.process:main",
        "signal_generator_param = courseworks.signal_generator_param:main",
        "reconstruction_param = courseworks.reconstruction_param:main",
        "signal_to_motor = courseworks.signal_to_motor:main",
        "indice_desempeno = courseworks.indice_desempeno:main",
        "Test_RED_Neuronal = courseworks.Test_RED_Neuronal:main",
        ],
    },
)
