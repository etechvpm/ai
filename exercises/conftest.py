"""Makes ``from _loader import load`` work from every exercise pack."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
