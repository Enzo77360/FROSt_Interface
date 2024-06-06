import tkinter as tk
from MotorCodes.Gui.interface_gui import MotorControllerGUI  # Importez votre classe MotorControllerGUI
from SpectroCodes.Gui_periodic_plot import SpectroGUI  # Importez votre classe SpectroGUI

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Application")

        # Créer les frames pour les instances de SpectroGUI1 et SpectroGUI2
        self.left_frame = tk.Frame(self.master, width=400, height=600)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side="left")

        self.right_frame = tk.Frame(self.master, width=400, height=600)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side="right")

        # Créer une instance de MotorControllerGUI dans le frame de gauche
        self.spectro1 = SpectroGUI(self.left_frame)

        # Créer une instance de SpectroGUI2 dans le frame de droite
        self.spectro2 = MotorControllerGUI(self.right_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
