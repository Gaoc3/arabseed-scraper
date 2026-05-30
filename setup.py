#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="arabseed-scraper",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",
        "rich>=10.0.0"
    ],
    entry_points={
        "console_scripts": [
            "arabseed-scraper=arabseed_scraper.cli:run_cli",
        ],
    },
)
