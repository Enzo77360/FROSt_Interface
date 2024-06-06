# -*- coding: utf-8 -*-
import sys
import numpy as np
import struct
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import libmozza.mozza_defines as MD
from libmozza.mozza import MozzaUSB, MozzaError

sys.path.append('.')

class SpectroGUI:
    def __init__(self, master):
        self.master = master
        #self.master.title("Spectro GUI")

        # Créer une figure Matplotlib
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # # Bouton Actualiser
        # self.update_button = tk.Button(self.master, text="Actualiser", command=self.update_plot)
        # self.update_button.pack()

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
            wnums, data, signal, reference = result
            self.ax1.clear()
            self.ax1.plot(wnums, data)
            self.ax1.set_xlabel(r'wavenumber [cm$^{-1}$]')
            self.ax1.set_ylabel(r'intensity [arb. units]')
            self.ax1.grid()

            smean, sstd = np.mean(signal), np.std(signal)
            rmean, rstd = np.mean(reference), np.std(reference)
            self.ax2.clear()
            self.ax2.plot(signal, label=r'signal mean=%.0f$\pm$%.1f' % (smean, sstd))
            self.ax2.plot(reference, label=r'reference mean=%.0f$\pm$%.1f' % (rmean, rstd))
            self.ax2.set_xlabel('Sample index')
            self.ax2.set_ylabel('Amplitude')
            self.ax2.grid()
            self.ax2.legend()

            self.canvas.draw()

    def update_spectro_gui(self):
        self.update_plot()
        self.master.after(3, self.update_spectro_gui)  # Actualiser toutes les 3 secondes


if __name__ == '__main__':
    print("Starting Spectro GUI...")
    root = tk.Tk()
    app = SpectroGUI(root)
    root.mainloop()
