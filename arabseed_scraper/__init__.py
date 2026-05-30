#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ArabSeed Scraper & Decrypter Library
-----------------------------------
A professional scraping API and CLI tool to search and extract decrypted
media links from ArabSeed and its mirrors.
"""

from .scraper import ArabSeedAPI, MIRRORS
from .cli import run_cli

__version__ = "1.0.0"
__author__ = "Antigravity Team"
__all__ = ["ArabSeedAPI", "MIRRORS", "run_cli"]
