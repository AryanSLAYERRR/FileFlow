import os
import sys
sys.path.append(os.getcwd())
from src.gui import FileFlowGUI

if __name__ == "__main__":
    app = FileFlowGUI()
    app.mainloop()
