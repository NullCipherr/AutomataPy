# main.py

import tkinter as tk
from model import CellularAutomatonModel
from view import CellularAutomatonUI

if __name__ == "__main__":
    root = tk.Tk()
    model = CellularAutomatonModel()
    app = CellularAutomatonUI(root, model)
    root.mainloop()
