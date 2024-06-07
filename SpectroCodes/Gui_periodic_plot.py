# -*- coding: utf-8 -*-
import sys
import numpy as np
import struct
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import libmozza.mozza_defines as MD
from libmozza.mozza import MozzaUSB, MozzaError
import csv
import os
sys.path.append('.')

class SpectroGUI:
    def __init__(self, master):
        self.master = master

        # Créer une figure Matplotlib
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Bouton Pause/Resume
        self.is_paused = False
        self.pause_button = tk.Button(self.master, text="Pause", command=self.toggle_pause)
        self.pause_button.pack()

        # # Bouton Save
        # self.save_button = tk.Button(self.master, text="Save Data", command=self.save_data)
        # self.save_button.pack()
        self.acquisition_count = 1  # Initialisation du compteur d'acquisitions

        # Initialisation du dispositif Mozza
        try:
            self.mozza = MozzaUSB()
            serials = self.mozza.get_serials()
            if serials:
                print(f'Found Mozza device with serials: {serials}')
                self.mozza.connect(serial=serials[0])
                self.mozza.set_wavenumber_array(np.arange(1e7 / 5000, 1e7 / 2000, 5))
                self.mozza.acquisition_params.trigger_source = MD.INTERNAL
                self.mozza.acquisition_params.trigger_frequency_Hz = 10000
                self.mozza.set_auto_params()
            else:
                messagebox.showerror("Erreur", "No Mozza device found")
                self.master.quit()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'initialisation du dispositif Mozza : {e}")
            self.master.quit()

        # Lancer la mise à jour périodique
        self.update_spectro_gui()

    def test_acquisition(self):
        try:
            bytes_to_read = self.mozza.begin_acquisition()
            raw = self.mozza.read_raw()
            signal, reference = self.mozza.separate_sig_ref(raw)
            self.mozza.end_acquisition()
            spectrum = self.mozza.process_spectrum(sig_data=signal, ref_data=reference)
            wnums = np.arange(1e7 / 5000, 1e7 / 2000, 5)
            return (wnums, spectrum, signal, reference)
        except MozzaError as e:
            print(e)
            return None

    def update_plot(self):
        result = self.test_acquisition()
        if result:
            self.wnums, self.data, self.signal, self.reference = result
            self.ax1.clear()
            self.ax1.plot(self.wnums, self.data)
            self.ax1.set_xlabel(r'wavenumber [cm$^{-1}$]')
            self.ax1.set_ylabel(r'intensity [arb. units]')
            self.ax1.grid()

            smean, sstd = np.mean(self.signal), np.std(self.signal)
            rmean, rstd = np.mean(self.reference), np.std(self.reference)
            self.ax2.clear()
            self.ax2.plot(self.signal, label=r'signal mean=%.0f$\pm$%.1f' % (smean, sstd))
            self.ax2.plot(self.reference, label=r'reference mean=%.0f$\pm$%.1f' % (rmean, rstd))
            self.ax2.set_xlabel('Sample index')
            self.ax2.set_ylabel('Amplitude')
            self.ax2.grid()
            self.ax2.legend()

            self.canvas.draw()

    def update_spectro_gui(self):
        if not self.is_paused:
            self.update_plot()
        self.master.after(3, self.update_spectro_gui)  # Actualiser toutes les 3 secondes

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")

    def save_data(self,folder_name):
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
