from setuptools import setup

setup(
    name='convert-twd',
    version='0.1.1',
    entry_points={
        'console_scripts': ['cvtwd=currency_converter_twd.CLI:run_cli'],
    },
    description='Command line tool for currency converter',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    author='Yu-Chen Xue',
    install_requires=[item.strip().replace('==', '>=') for item in open('./requirements.txt').readlines()],
    packages=['currency_converter_twd'],
    package_data={'': ['*.csv']},
    include_package_data=True,
)
