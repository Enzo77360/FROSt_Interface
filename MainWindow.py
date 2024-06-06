import tkinter as tk
from MotorCodes.Gui.interface_gui import MotorControllerGUI  # Importez votre classe MotorControllerGUI
from SpectroCodes.Gui_Periodic_plot import SpectroGUI
import threading

class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Application")

        # Créer les frames pour les instances de SpectroGUI1 et MotorControllerGUI
        self.left_frame = tk.Frame(self.master, width=450, height=650)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side="left")

        self.right_frame = tk.Frame(self.master, width=450, height=650)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side="right")

        # Créer une instance de MotorControllerGUI dans le frame de droite
        self.motor_controller = MotorControllerGUI(self.right_frame)

        # Créer une instance de SpectroGUI dans le frame de gauche
        self.spectro_gui = SpectroGUI(self.left_frame)



if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
