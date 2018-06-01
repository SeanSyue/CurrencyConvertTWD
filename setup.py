from setuptools import setup

setup(
    name='currency_converter',
    version='0.1.0',
    entry_points={
        'console_scripts': ['currency_converter=cli.cli_test:run_cli'],
    },
    description='Command line tool for currency converter',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    author='Yu-Chen Xue',
    packages=['cli'],
    include_package_data=True,
    zip_safe=False)
