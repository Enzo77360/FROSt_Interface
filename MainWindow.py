import tkinter as tk
from PIL import Image, ImageTk  # Importez les modules nécessaires de PIL
from MotorCodes.Gui.interface_gui import MotorControllerGUI  # Importez votre classe MotorControllerGUI
from SpectroCodes.Gui_Periodic_plot import SpectroGUI


class MainApplication:
    def __init__(self, master):
        self.master = master
        self.master.title("FROSt Interface")

        # Créer les frames pour les instances de SpectroGUI1 et MotorControllerGUI
        self.left_frame = tk.Frame(self.master, width=700, height=700)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(side="left")

        self.right_frame = tk.Frame(self.master, width=450, height=700)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side="right")

        # Charger, redimensionner et afficher le logo
        original_logo = Image.open(r"C:\Users\enzos\OneDrive\Pictures\LogoINRS.png")  # Chemin réel de votre logo
        resized_logo = original_logo.resize((120, 83), Image.BILINEAR)  # Redimensionner l'image à 80x60 pixels
        self.logo_image = ImageTk.PhotoImage(resized_logo)
        self.logo_label = tk.Label(self.master, image=self.logo_image)
        self.logo_label.place(x=950, y=600)

        original_logo_alls = Image.open(r"C:\Users\enzos\OneDrive\Pictures\alls.png")  # Chemin réel de votre logo
        resized_logo_alls = original_logo_alls.resize((200, 60), Image.BILINEAR)  # Redimensionner l'image à 80x60 pixels
        self.logo_image_alls = ImageTk.PhotoImage(resized_logo_alls)
        self.logo_label_alls = tk.Label(self.master, image=self.logo_image_alls)
        self.logo_label_alls.place(x=700, y=620)

        # Créer une instance de MotorControllerGUI dans le frame de droite
        self.motor_controller = MotorControllerGUI(self.right_frame)

        # Créer une instance de SpectroGUI dans le frame de gauche
        self.spectro_gui = SpectroGUI(self.left_frame)

        # Lier la mise à jour du spectrogramme à l'événement de mouvement du moteur
        self.motor_controller.set_spectro_gui(self.spectro_gui)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
