import os
from codecs import open
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'DTMicroscope/__version__.py')) as f:
    __version__ = f.read().split("'")[1]

with open("README.md", "r") as fr:
    long_description = fr.read()

setup(
    name='DTMicroscope',
    version=__version__,
    description='Digital Twin Microscope',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pycroscopy/DTMicroscope',
    author='Rama Vasudevan, Boris Slautin, Utkarsh Pratiush, Gerd Duscher',
    license='MIT',
    packages=find_packages(exclude='tests'),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'run_server_afm=DTMicroscope.commands:run_server_afm', 
            'run_server_stem=DTMicroscope.commands:run_server_stem',   # Point to the correct module and function
        ],
    },
)
