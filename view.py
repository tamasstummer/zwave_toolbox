import tkinter as tk
import tkinter.font as tkFont

class View(tk.Tk):
    def __init__(self, number_of_screen = 0):
        super().__init__()
        self.title("Z-Wave Toolbox")
        self.geometry("800x480")
        self.resizable(True, True)



def main():
    print("main")

if __name__ == "__main__":
    main()

