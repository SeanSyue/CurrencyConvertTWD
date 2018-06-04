from setuptools import setup, find_packages

setup(
    name='convert-twd',
    version='0.1.0',
    entry_points={
        'console_scripts': ['cvtwd=currency_converter_twd.CLI:run_cli'],
    },
    description='Command line tool for currency converter',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    author='Yu-Chen Xue',
    packages=['currency_converter_twd'],
    include_package_data=True,
    zip_safe=False)
