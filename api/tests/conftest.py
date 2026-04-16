import sys
import os

# Make `import main` resolve to api/main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
