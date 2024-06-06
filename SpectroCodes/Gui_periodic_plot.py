import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from SpectroCodes.libmozza.Mozza import MozzaSpectro
from SpectroCodes.libmozza.spectro import Acquisition, TriggerTimeoutError


class SpectroGUI:
    def __init__(self, master):
        self.master = master
        #self.master.title("Spectro GUI")
        #self.master.geometry("500x600")

        # Créer une figure Matplotlib
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()

        # Bouton Actualiser
        self.update_button = tk.Button(self.master, text="Actualiser", command=self.update_plot)
        self.update_button.pack()

        # # Bouton Quitter
        # self.quit_button = tk.Button(self.master, text="Quitter", command=self.master.quit)
        # self.quit_button.pack()

        # Créer une instance de MozzaSpectro
        self.spectro = MozzaSpectro()

        # Obtenez les numéros de série des périphériques connectés
        serials = MozzaSpectro.get_serials()
        print(f"Available devices: {serials}")

        if not serials:
            raise Exception("No devices found")

        # Connectez-vous au périphérique en utilisant le numéro de série
        serial = serials[0]  # Par exemple, connectez-vous au premier périphérique
        self.spectro.connect_device(serial)

        # Définir le temps d'exposition (si nécessaire)
        self.spectro.set_exposure(0.1)  # 0.1 secondes

        # Essayer sans déclencheur externe
        try:
            self.spectro.set_ext_trigger(False, apply=True)
        except Exception as e:
            print(f"Error setting external trigger: {e}")

        # Définir les limites de la table spectrale
        try:
            self.spectro.acquisition = Acquisition(start=0, stop=3499)  # Exemple de méthode possible
        except AttributeError as e:
            print(f"Error setting acquisition range: {e}")

        # Vérifiez la correction d'amplitude
        if not self.spectro.load_amp_correction(int(serial.split('#')[1])):
            print("Amplitude correction file not found, proceeding without it.")

        # Mettre à jour le plot périodiquement
        self.update_periodically()

    def update_plot(self):
        # Acquérir un nouveau spectre
        try:
            spectrum = self.spectro._acquire_spectrum(background_mode=False)
        except TriggerTimeoutError:
            print("Trigger timeout error: External trigger not detected.")
            return
        except Exception as e:
            print(f"Error acquiring spectrum: {e}")
            return

        # Vérifier si le spectre est acquis
        if spectrum is not None:
            print("Spectrum acquired successfully.")

            # Récupérer les longueurs d'onde
            lambdas = self.spectro.lambdas

            if lambdas is not None:
                # Vérifier que les dimensions sont compatibles
                if len(lambdas) == len(spectrum):
                    # Mettre à jour le tracé avec le nouveau spectre
                    self.ax.clear()  # Effacer le contenu actuel de la figure
                    self.ax.plot(lambdas, spectrum)
                    self.ax.set_title('Spectrum Intensity vs Wavelength')
                    self.ax.set_xlabel('Wavelength (nm)')
                    self.ax.set_ylabel('Intensity')
                    self.canvas.draw()
                else:
                    print("Error: Dimensions of wavelength and spectrum data are not compatible.")
                    print(len(lambdas), len(spectrum))
            else:
                print("Failed to retrieve wavelength data.")
        else:
            print("Failed to acquire spectrum.")

    def update_periodically(self):
        self.update_plot()
        self.master.after(300, self.update_periodically)  # Actualiser toutes les 3 secondes

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectroGUI(root)
    root.mainloop()
