import toga
#from src.expensetracker.app import main
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from .app import main

if __name__ == "__main__":
    app = main()
    app.main_loop()
