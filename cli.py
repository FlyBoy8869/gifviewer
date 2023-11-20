"""Entry point"""

import argparse

import gifviewer.settings as settings

from gifviewer.__main__ import main

parser = argparse.ArgumentParser()
parser.add_argument("--no-confirm-exit", action="store_true")
args = parser.parse_args()
settings.args = args

if __name__ == "__main__":
    main()
