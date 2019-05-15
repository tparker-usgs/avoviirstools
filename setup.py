"""
avoviirstools -- tools for maintaining AVO VIIRS processing

"""

from setuptools import setup, find_packages
from avoviirstools import __version__

DOCSTRING = __doc__.split("\n")

setup(
    name="avoviirstools",
    version=__version__,
    author="Tom Parker",
    author_email="tparker@usgs.gov",
    description=(DOCSTRING[1]),
    license="CC0",
    url="http://github.com/tparker-usgs/avoviirstools",
    packages=find_packages(),
    long_description='\n'.join(DOCSTRING[3:]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    ],
    install_requires=[
        'tomputils>=1.12.16',
        'avoviirsprocessor',
        'humanize'
    ],
    dependency_links=[
        'git+https://github.com/tparker-usgs/avoviirsprocessor.git#egg=avoviirsprocessor-3.16.3', # NOQA
    ],
    entry_points={
        'console_scripts': [
            'sniff_sdr = avoviirstools.sniff_sdr:main',
            'sniff_update = avoviirstools.sniff_update:main',
            'pass_plotter = avoviirstools.pass_plotter:main',
            'dashboard = avoviirstools.dashboard:main'
        ]
    }

)
