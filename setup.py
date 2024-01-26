from setuptools import setup, find_packages

# Auto generate install reqs

with open('requirements.txt','r') as f:
    REQ_LINES = list(f.readlines())

for i in REQ_LINES:
    i += ','

setup(
    name='Thrusty',
    version='0.0.0',
    url='',
    author='Some Joe',
    author_email='joe.burge.iii@gmail.com',
    description='Thrust Modeling',
    packages=find_packages(exclude='testing.test'),
    install_requires=REQ_LINES,
)
