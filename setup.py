from setuptools import setup

setup(
    name='qualtrics_collaboration',
    description='An easy way for NYU students collaborate on Qualtrics surveys.',
    version='1.0',
    packages=['qualtrics_collaboration'],
    install_requires=[
        'selenium',
        'requests',
        'scipy'
    ],
    author = 'Jacob Padilla'
)
