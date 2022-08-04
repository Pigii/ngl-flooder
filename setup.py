from setuptools import setup, find_packages

setup(
    name='ngl-flooder',
    version='0.1.0',
    packages=find_packages(include=['ngl-flooder', 'ngl-flooder.*']),
    install_requires=[
        'requests',
    ]
)
