import tkinter as tk
from tkinter import messagebox
from MotorCodes.Gui.Methods_gui import KCubeDCServoController
import threading
import os
from Traces.Trace_FROSt import HeatmapGUI
from datetime import datetime
# Importer la classe SpectroGUI
from SpectroCodes.Gui_Periodic_plot import SpectroGUI

C_MM_PER_FS = 3e-4  # La vitesse de la lumière en mm/fs (3e8 m/s = 3e5 mm/s = 3e-4 mm/fs)

class MotorControllerGUI:
    def __init__(self, master):
        self.master = master
        # self.master.geometry("400x700") # Attention à l'enlever après
        self.controller = KCubeDCServoController()  # Créer une instance du contrôleur de moteur
        self.connected_device = None  # Variable pour stocker le périphérique connecté
        self.current_position = 0.0  # Initialiser la position actuelle du moteur
        self.spectro_gui = None # Instance de SpectroGUI pour la mise à jour du spectrogramme
        self.data_folder = r"C:\Users\enzos\PycharmProjects\FROSt_Interface"

        # Variables pour stocker les valeurs de départ, d'arrivée et de taille des étapes
        self.home_position_fs = tk.StringVar()
        self.start_position = tk.StringVar()
        self.end_position = tk.StringVar()
        self.step_size = tk.StringVar()
        self.step = tk.StringVar()

        # Appliquer le thème "xpnative"
        self.master.option_add('*TCombobox*Listbox.background', '#FFFFFF')
        self.master.option_add('*TCombobox*Listbox.foreground', '#000000')
        self.master.option_add('*TCombobox*Listbox.selectBackground', '#0078D7')
        self.master.option_add('*TCombobox*Listbox.selectForeground', '#FFFFFF')
        self.master.option_add('*TCombobox*Listbox.selectBorderWidth', 0)
        self.master.option_add('*TCombobox.font', ('Segoe UI', 10))

        # Créer et placer les widgets dans la fenêtre
        self.create_widgets()

    def create_widgets(self):
        # Frame pour la liste des périphériques
        frame_devices = tk.LabelFrame(self.master, text="Périphériques disponibles", padx=10, pady=10)
        frame_devices.pack(padx=10, pady=10, fill="x")

        # Boîte de liste pour afficher les périphériques
        self.listbox_devices = tk.Listbox(frame_devices, height=2)
        self.listbox_devices.pack(padx=10, pady=5, fill="x")
        self.listbox_devices.bind("<Double-Button-1>", self.select_device_from_list)

        # Bouton pour mettre à jour la liste des périphériques
        self.button_refresh = tk.Button(frame_devices, text="Actualiser", command=self.refresh_devices)
        self.button_refresh.pack(pady=5)

        # Frame pour les paramètres du moteur
        frame_params = tk.LabelFrame(self.master, text="Paramètres du moteur", padx=10, pady=10)
        frame_params.pack(padx=10, pady=10, fill="x")

        # Libellé et champ de saisie pour l'ID du périphérique
        self.label_device = tk.Label(frame_params, text="ID du périphérique:")
        self.label_device.pack(anchor="w")
        self.entry_device = tk.Entry(frame_params)
        self.entry_device.pack(fill="x", pady=5)

        # Bouton pour initialiser le moteur
        self.button_init = tk.Button(frame_params, text="Initialiser", command=self.initialize_motor)
        self.button_init.pack(fill="x", padx=5, pady=5)

        # Step fs:
        # Libellé et champ de saisie pour la taille Step
        self.label_step = tk.Label(frame_params, text="Step (fs):")
        self.label_step.pack(anchor="w")
        self.entry_step = tk.Entry(frame_params, textvariable=self.step)
        self.entry_step.pack(fill="x", pady=5)

        # Frame pour contenir les boutons Backward et Forward
        frame_buttons = tk.Frame(frame_params)
        frame_buttons.pack(fill="x", padx=5, pady=5)

        # Ajouter les boutons Backward et Forward sous le bouton Initialiser
        self.button_backward = tk.Button(frame_buttons, text="Backward", command=self.move_backward)
        self.button_forward = tk.Button(frame_buttons, text="Forward", command=self.move_forward)

        # Pack les boutons Backward et Forward sur la même ligne
        self.button_backward.pack(side="left", padx=5)
        self.button_forward.pack(side="left", padx=5)

        # Étiquette pour afficher la position actuelle
        self.label_current_position = tk.Label(frame_buttons,
                                               text=f"Position actuelle (fs): {self.current_position:.2f}")
        self.label_current_position.pack(side="left", padx=5, pady=5)

        # Ajouter un bouton Set sous les boutons Backward et Forward
        self.button_set = tk.Button(frame_buttons, text="Set", command=self.set_position_to_zero)
        self.button_set.pack(side="left", padx=5, pady=5)



        # Libellé et champ de saisie pour la position de départ
        self.label_start = tk.Label(frame_params, text="Position de départ (fs):")
        self.label_start.pack(anchor="w")
        self.entry_start = tk.Entry(frame_params, textvariable=self.start_position)
        self.entry_start.pack(fill="x", pady=5)

        # Libellé et champ de saisie pour la position de fin
        self.label_end = tk.Label(frame_params, text="Position de fin (fs):")
        self.label_end.pack(anchor="w")
        self.entry_end = tk.Entry(frame_params, textvariable=self.end_position)
        self.entry_end.pack(fill="x", pady=5)

        # Libellé et champ de saisie pour la taille des étapes
        self.label_step_size = tk.Label(frame_params, text="Taille des étapes (fs):")
        self.label_step_size.pack(anchor="w")
        self.entry_step_size = tk.Entry(frame_params, textvariable=self.step_size)
        self.entry_step_size.pack(fill="x", pady=5)

        # Ajouter les traces pour valider automatiquement les entrées
        self.home_position_fs.trace_add("write", self.validate_entries)
        self.start_position.trace_add("write", self.validate_entries)
        self.end_position.trace_add("write", self.validate_entries)
        self.step_size.trace_add("write", self.validate_entries)

        # Frame pour les boutons d'action
        frame_actions = tk.Frame(self.master, padx=5, pady=5)
        frame_actions.pack(padx=5, pady=5, fill="x")

        # Bouton pour démarrer le déplacement
        self.button_move = tk.Button(frame_actions, text="Déplacer", command=self.start_movement)
        self.button_move.pack(side="left", padx=5, pady=5)

        # Bouton pour quitter
        self.button_quit = tk.Button(frame_actions, text="Quitter", command=self.quit_program)
        self.button_quit.pack(side="left", padx=5, pady=5)

        # Créer le bouton "Next" en bas à droite
        self.next_button = tk.Button(self.master, text="   Next   ", command=self.create_heatmap_gui)
        self.next_button.pack(side="right", padx=5, pady=5)

        # Fonction pour mettre à jour l'affichage de la position actuelle à 0.00 fs
    def set_position_to_zero(self):
        self.label_current_position.config(text="Position actuelle (fs): 0.00")

    def update_position_labels(self):
        current_fs = self.current_position / (C_MM_PER_FS / 2)
        self.label_current_position.config(text=f"Position actuelle (fs): {current_fs:.2f}")

    def move_backward(self):
        threading.Thread(target=self._move, args=(-1,)).start()

    def move_forward(self):
        threading.Thread(target=self._move, args=(1,)).start()

    def _move(self, direction):
        try:
            if not self.connected_device:
                raise Exception("Veuillez connecter et initialiser le moteur avant de le déplacer.")
            step_fs = float(self.step.get())  # Récupérer la taille de l'étape en femtosecondes
            step_mm = step_fs * C_MM_PER_FS * direction / 2  # Convertir en millimètres et appliquer la direction
            new_position = self.current_position + step_mm  # aller- retour
            self.controller.configure_movement(new_position, 1)
            self.controller.move_motor()
            self.controller.wait_for_completion()
            self.current_position = new_position  # Mettre à jour la position actuelle
            self.update_position_labels()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def set_spectro_gui(self, spectro_gui):
        self.spectro_gui = spectro_gui

    def refresh_devices(self):
        self.listbox_devices.delete(0, tk.END)
        for device in self.controller.get_device_list():
            self.listbox_devices.insert(tk.END, device)

    def select_device_from_list(self, event):
        selected_device = self.listbox_devices.get(self.listbox_devices.curselection())
        self.entry_device.delete(0, tk.END)
        self.entry_device.insert(0, selected_device)

    def initialize_motor(self):
        try:
            device_id = self.entry_device.get()
            if not self.connected_device:
                self.controller.connect_motor(device_id)
                self.connected_device = device_id
            self.controller.initialize_motor()
            self.current_position = 0.0  # Réinitialiser la position actuelle à 0 après initialisation
            messagebox.showinfo("Initialisation", "Le moteur a été initialisé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def validate_entries(self, *args):
        try:
            self.home_position_val = float(self.current_position)
            self.start_position_val = float(self.start_position.get()) * C_MM_PER_FS / 2  # aller-retour
            self.end_position_val = float(self.end_position.get()) * C_MM_PER_FS / 2
            self.step_size_val = float(self.step_size.get()) * C_MM_PER_FS / 2
        except ValueError:
            # Ne rien faire si les valeurs ne sont pas encore toutes remplies ou sont invalides
            pass

    def start_movement(self):
        threading.Thread(target=self._start_movement).start()

    def _start_movement(self):
        try:
            if (not hasattr(self, 'home_position_val') or not hasattr(self, 'start_position_val')
                    or not hasattr(self, 'end_position_val') or not hasattr(self, 'step_size_val')):
                raise ValueError("Veuillez définir la position HOME, les positions de départ et de fin, ainsi que la taille des étapes.")

            device_id = self.connected_device
            if not device_id:
                raise Exception("Veuillez connecter et initialiser le moteur avant de commencer le mouvement.")

            home_position = self.home_position_val
            current_position = home_position + self.start_position_val
            end_position = home_position + self.end_position_val
            step_size = self.step_size_val

            # Obtenir la date et l'heure actuelles
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Nom du dossier pour enregistrer les acquisitions avec le temps du moment de la création
            folder_name = os.path.join(self.data_folder, f"Acquisitions\\Acquisitions_{current_time}")

            # Vérifier si le dossier existe, sinon le créer
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            while current_position <= end_position:
                self.controller.configure_movement(current_position, 1)
                self.controller.move_motor()
                self.controller.wait_for_completion()
                self.current_position = current_position  # Mettre à jour la position actuelle
                self.spectro_gui.update_all_params()
                self.spectro_gui.save_data(folder_name)

                current_position += step_size
            messagebox.showinfo("Information", "Acquisition terminée !")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def create_heatmap_gui(self):
        # Créer la fenêtre HeatmapGUI lorsque le bouton "Next" est pressé
        heatmap_window = tk.Toplevel(self.master)
        heatmap_window.title("Heatmap de l'intensité en fonction du wavenumber")

        # Instancier HeatmapGUI dans la nouvelle fenêtre
        HeatmapGUI(heatmap_window)

    def quit_program(self):
        self.master.quit()
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = MotorControllerGUI(root)
    root.mainloop()
