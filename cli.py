"""Entry point"""

import argparse

import gifviewer.settings as settings

from gifviewer.__main__ import main

parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-confirm-exit", action="store_true", help="Bypass exit confirmation."
)
cl_args = parser.parse_args()
settings.cl_args = cl_args

if __name__ == "__main__":
    main()
