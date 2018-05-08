'''
Installation script.
'''

from setuptools import setup, find_packages

# List of necessary packages
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Install!
setup(
    name="oncotools",
    version="2.0.1",

    # packages=['oncotools'],
    packages=find_packages(where='src'),
    package_dir={'oncotools': 'src/oncotools'},

    # Make sure required packages are installed
    install_requires=required,

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.md', '*.rst'],
    },

    # metadata for upload to PyPI
    author="Pranav Lakshminarayanan",
    author_email="plakshm1@jhu.com",
    description="Oncospace Python Tools"
)
