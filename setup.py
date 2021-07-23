from setuptools import setup

help('modules')

setup(
    name='ToxAssign',
    entry_points={
        'console_scripts': [
            'toxassign = ToxAssign.Automation:main',
        ],
    }
)