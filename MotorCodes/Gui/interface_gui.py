import tkinter as tk
from tkinter import messagebox
from MotorCodes.Gui.Methods_gui import KCubeDCServoController
import time
import threading

class MotorControllerGUI:
    def __init__(self, master):
        self.master = master
        self.controller = KCubeDCServoController()  # Créer une instance du contrôleur de moteur
        self.connected_device = None  # Variable pour stocker le périphérique connecté
        self.current_position = 0.0  # Initialiser la position actuelle du moteur

        # Variables pour stocker les valeurs de départ, d'arrivée et de taille des étapes
        self.start_position = tk.StringVar()
        self.end_position = tk.StringVar()
        self.step_size = tk.StringVar()

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
        self.listbox_devices = tk.Listbox(frame_devices, height=5)
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

        # Ajouter les boutons Backward et Forward sous le bouton Initialiser
        self.button_backward = tk.Button(frame_params, text="Backward", command=self.move_backward)
        self.button_forward = tk.Button(frame_params, text="Forward", command=self.move_forward)

        # Pack les boutons Backward et Forward sur la même ligne
        self.button_backward.pack(side="left", padx=5, pady=5)
        self.button_forward.pack(side="left", padx=5, pady=5)

        # Libellé et champ de saisie pour la position de départ
        self.label_start = tk.Label(frame_params, text="Position de départ (mm):")
        self.label_start.pack(anchor="w")
        self.entry_start = tk.Entry(frame_params, textvariable=self.start_position)
        self.entry_start.pack(fill="x", pady=5)

        # Libellé et champ de saisie pour la position de fin
        self.label_end = tk.Label(frame_params, text="Position de fin (mm):")
        self.label_end.pack(anchor="w")
        self.entry_end = tk.Entry(frame_params, textvariable=self.end_position)
        self.entry_end.pack(fill="x", pady=5)

        # Libellé et champ de saisie pour la taille des étapes
        self.label_step = tk.Label(frame_params, text="Taille des étapes (mm):")
        self.label_step.pack(anchor="w")
        self.entry_step = tk.Entry(frame_params, textvariable=self.step_size)
        self.entry_step.pack(fill="x", pady=5)

        # Ajouter les traces pour valider automatiquement les entrées
        self.start_position.trace_add("write", self.validate_entries)
        self.end_position.trace_add("write", self.validate_entries)
        self.step_size.trace_add("write", self.validate_entries)

        # Frame pour les boutons d'action
        frame_actions = tk.Frame(self.master, padx=10, pady=10)
        frame_actions.pack(padx=10, pady=10, fill="x")

        # Bouton pour démarrer le déplacement
        self.button_move = tk.Button(frame_actions, text="Déplacer", command=self.start_movement)
        self.button_move.pack(side="left", padx=5, pady=5)

        # Bouton pour quitter
        self.button_quit = tk.Button(frame_actions, text="Quitter", command=self.quit_program)
        self.button_quit.pack(side="left", padx=5, pady=5)

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

    def move_backward(self):
        threading.Thread(target=self._move, args=(-0.5,)).start()

    def move_forward(self):
        threading.Thread(target=self._move, args=(0.5,)).start()

    def _move(self, step):
        try:
            if not self.connected_device:
                raise Exception("Veuillez connecter et initialiser le moteur avant de le déplacer.")
            new_position = self.current_position + step
            self.controller.configure_movement(new_position, 1)
            self.controller.move_motor()
            self.controller.wait_for_completion()
            self.current_position = new_position  # Mettre à jour la position actuelle
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def validate_entries(self, *args):
        try:
            self.start_position_val = float(self.start_position.get())
            self.end_position_val = float(self.end_position.get())
            self.step_size_val = float(self.step_size.get())
        except ValueError:
            # Ne rien faire si les valeurs ne sont pas encore toutes remplies ou sont invalides
            pass

    def start_movement(self):
        threading.Thread(target=self._start_movement).start()

    def _start_movement(self):
        try:
            if not hasattr(self, 'start_position_val') or not hasattr(self, 'end_position_val') or not hasattr(self, 'step_size_val'):
                raise ValueError("Veuillez définir les positions de départ, de fin et la taille des étapes.")

            device_id = self.connected_device
            if not device_id:
                raise Exception("Veuillez connecter et initialiser le moteur avant de le déplacer.")

            current_position = self.start_position_val
            while current_position <= self.end_position_val:
                self.controller.configure_movement(current_position, 2)  # Configurer pour 2 secondes à chaque étape
                self.controller.move_motor()
                self.controller.wait_for_completion()
                time.sleep(2)  # Attendre 2 secondes à chaque étape #TODO add trigger
                current_position += self.step_size_val

            messagebox.showinfo("Déplacement", "Déplacement terminé.")
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def quit_program(self):
        self.master.quit()
