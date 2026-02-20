#!/usr/bin/env python3
"""
AudioGuide __main__.py - enables python -m audioguide
"""

from audioguide.cli import main

if __name__ == '__main__':
    import sys
    sys.exit(main())
