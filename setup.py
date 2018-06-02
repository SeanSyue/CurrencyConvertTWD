from setuptools import setup, find_packages

setup(
    name='cvt',
    version='0.1.0',
    entry_points={
        'console_scripts': ['cvt=src.CLI:run_cli'],
    },
    description='Command line tool for currency converter',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    author='Yu-Chen Xue',
    packages=['src'],
    include_package_data=True,
    zip_safe=False)
