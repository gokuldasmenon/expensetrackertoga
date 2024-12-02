from setuptools import setup

setup(
    name='ExpenseTracker',
    version='1.0',
    packages=['app'],
    package_dir={'app': 'app'},
    include_package_data=True,
    install_requires=[
        'toga',
        'toga-core',
        'toga-winforms',
    ],
)
