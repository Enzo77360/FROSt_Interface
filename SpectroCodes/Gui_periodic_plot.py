import sys
import numpy as np
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import libmozza.mozza_defines as md
from libmozza.mozza import MozzaUSB, MozzaError
import csv
import os


sys.path.append('.')

class SpectroGUI:
    def __init__(self, master):
        self.master = master
        # self.master.title("Spectro GUI")
        # self.master.configure(bg='#f0f0f0')

        # Initialisation de param_entries
        self.param_entries = {}

        # Créer une figure Matplotlib
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Ajout des entrées pour les paramètres
        self.create_parameter_controls()

        self.acquisition_count = 1  # Initialisation du compteur d'acquisitions
        self.is_first_apply = True  # Variable pour suivre si Apply a été pressé pour la première fois
        self.is_paused = True  # Variable pour suivre si le système est en pause ou en marche

        # Initialisation du dispositif Mozza
        try:
            self.mozza = MozzaUSB()
            serials = self.mozza.get_serials()
            if serials:
                print(f'Found Mozza device with serials: {serials}')
                self.mozza.connect(serial=serials[0])
                self.set_initial_params()
            else:
                messagebox.showerror("Erreur", "No Mozza device found")
                self.master.quit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'initialisation du dispositif Mozza : {e}")
            self.master.quit()

        # Lancer la mise à jour périodique
        self.update_spectro_gui()

    def set_initial_params(self):
        self.mozza.set_wavenumber_array(np.arange(1e7 / 5000, 1e7 / 2000, 5))
        self.mozza.acquisition_params.trigger_source = md.INTERNAL
        self.mozza.acquisition_params.trigger_frequency_Hz = 10000
        self.mozza.set_auto_params(point_repetition=1, reference_offset=0,
                                   signal_high_gain=False, reference_high_gain=False,
                                   trigger_to_laser_us=0, acquisition_time_us=10)

    def create_parameter_controls(self):
        param_frame = tk.LabelFrame(self.master, text="Acquisition Parameters", padx=5, pady=5, bg='#f0f0f0', font=("Arial", 10))
        param_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Ligne pour les paramètres des longueurs d'onde
        wave_frame = tk.Frame(param_frame, bg='#f0f0f0')
        wave_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.create_param_entry(wave_frame, "Wavelength Initial (nm)", "2000")
        self.create_param_entry(wave_frame, "Wavelength Final (nm)", "5000")
        self.create_param_entry(wave_frame, "Wavelength Step (nm)", "5")

        # Ligne pour les autres paramètres
        other_frame = tk.Frame(param_frame, bg='#f0f0f0')
        other_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.create_param_entry(other_frame, "Trigger Frequency (Hz)", "10000")
        self.create_param_entry(other_frame, "Acquisition Time (us)", "10")
        self.create_param_entry(other_frame, "Trigger to Laser (us)", "0")

        # Cadre pour les boutons
        button_frame = tk.Frame(param_frame, bg='#f0f0f0')
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Bouton Pause/Resume
        # self.is_paused = True
        self.pause_button = tk.Button(button_frame, text="Start", command=self.toggle_pause, font=("Arial", 10),
                                      bg='#4CAF50', fg='white', state=tk.DISABLED)
        self.pause_button.pack(side=tk.RIGHT)

        set_global_button = tk.Button(button_frame, text="Apply", command=self.update_all_params,
                                      font=("Arial", 10), bg='#2196F3', fg='white')
        set_global_button.pack(side=tk.RIGHT, padx=5)



    def create_param_entry(self, frame, label_text, default_value, label_width=19, entry_width=10):
        label = tk.Label(frame, text=label_text, width=label_width, anchor='w', font=("Arial", 8), bg='#f0f0f0')
        label.pack(side=tk.LEFT, padx=5, pady=5)

        entry = tk.Entry(frame, width=entry_width, font=("Arial", 10))
        entry.insert(0, default_value)
        entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.param_entries[label_text] = entry

    def update_all_params(self):
        if self.is_first_apply:
            self.is_first_apply = False  # Mettre à jour pour indiquer que Apply a été pressé pour la première fois
            self.pause_button.config(state=tk.NORMAL)  # Activer le bouton Start une fois que Apply est pressé

        # Récupérer les valeurs des paramètres
        self.wavelength_initial = float(self.param_entries["Wavelength Initial (nm)"].get())
        self.wavelength_final = float(self.param_entries["Wavelength Final (nm)"].get())
        self.wavenumber_step = float(self.param_entries["Wavelength Step (nm)"].get())
        self.trigger_frequency = int(self.param_entries["Trigger Frequency (Hz)"].get())
        self.acquisition_time = int(self.param_entries["Acquisition Time (us)"].get())
        self.trigger_to_laser = int(self.param_entries["Trigger to Laser (us)"].get())
        # self.mozza.set_auto_params(self.acquisition_time)

    def test_acquisition(self):
        wls_nm = (1e7 / self.wavelength_final, 1e7 / self.wavelength_initial )
        wnums = np.arange(1e7 / wls_nm[1], 1e7 / wls_nm[0], self.wavenumber_step)
        self.mozza.set_wavenumber_array(wnums)
        self.mozza.acquisition_params.trigger_frequency_Hz = self.trigger_frequency
        # self.mozza.set_auto_params()
        bytes_to_read = self.mozza.begin_acquisition()
        raw = self.mozza.read_raw()
        signal, reference = self.mozza.separate_sig_ref(raw)
        self.mozza.end_acquisition()
        spectrum = self.mozza.process_spectrum(sig_data=signal, ref_data=reference)
        # wnums = np.arange(1e7 / 5000, 1e7 / 2000, 5)
        return wnums, spectrum, signal, reference

    def update_plot(self):
        result = self.test_acquisition()
        if result:
            self.wnums, self.data, self.signal, self.reference = result

            smean, sstd = np.mean(self.signal), np.std(self.signal)
            rmean, rstd = np.mean(self.reference), np.std(self.reference)

            self.ax1.clear()  # Effacer le subplot 1 en premier
            self.ax1.plot(self.signal, label=r'signal mean=%.0f$\pm$%.1f' % (smean, sstd))
            self.ax1.plot(self.reference, label=r'reference mean=%.0f$\pm$%.1f' % (rmean, rstd))
            # self.ax1.set_xlabel('Sample index')
            self.ax1.set_ylabel('Amplitude')
            self.ax1.grid()
            self.ax1.legend()

            self.ax2.clear()  # Effacer le subplot 2 en second
            self.ax2.plot(self.wnums, self.data)
            self.ax2.set_xlabel(r'wavelength [nm]')
            self.ax2.set_ylabel(r'intensity [arb. units]')
            self.ax2.grid()

            self.canvas.draw()

    def update_spectro_gui(self):
        if not self.is_paused:
            self.update_plot()
        self.master.after(3, self.update_spectro_gui)

    def toggle_pause(self):
        if self.is_first_apply:  # Vérifier si Apply a été pressé pour la première fois
            messagebox.showwarning("Attention", "Veuillez d'abord appliquer les paramètres.")
        else:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_button.config(text="Start", bg='#4CAF50')
            else:
                self.pause_button.config(text="Stop", bg='#F44336')


    def save_data(self, folder_name):
        if hasattr(self, 'wnums') and hasattr(self, 'data'):
            # Chemin du fichier basé sur le compteur d'acquisitions
            file_name = f"{self.acquisition_count}_acquisition.csv"
            file_path = os.path.join(folder_name, file_name)

            # Enregistrement des données dans le fichier spécifié
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Wavenumber [cm^-1]', 'Intensity [arb. units]', 'Signal', 'Reference'])
                for i in range(len(self.wnums)):
                    writer.writerow([self.wnums[i], self.data[i], self.signal[i], self.reference[i]])

            # Augmentation du compteur d'acquisitions
            self.acquisition_count += 1

            # messagebox.showinfo("Save Data", "Data saved successfully!")
        else:
            messagebox.showwarning("Save Data", "No data to save!")

if __name__ == '__main__':
    print("Starting Spectro GUI...")
    root = tk.Tk()
    app = SpectroGUI(root)
    root.mainloop()
