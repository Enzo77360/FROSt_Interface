import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from tkinter import Tk, Button, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HeatmapGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Heatmap de l'intensité en fonction du wavenumber")

        # Chemin du dossier contenant les acquisitions
        self.base_directory = "Acquisitions"

        # Obtenir le dernier dossier créé dans le répertoire "Acquisitions"
        self.directory = self.get_latest_directory(self.base_directory)

        if not self.directory:
            raise Exception("No directories found in the base directory")

        # Liste des fichiers CSV dans le dossier
        self.files = glob.glob(os.path.join(self.directory, '*.csv'))

        if not self.files:
            raise Exception("No CSV files found in the latest directory")

        # Initialiser une liste pour stocker les valeurs d'intensité de chaque fichier
        self.intensity_data = []

        # Parcourir chaque fichier CSV dans la liste et extraire les valeurs d'intensité
        for file in self.files:
            # Lire le fichier CSV en tant que DataFrame pandas
            df = pd.read_csv(file)

            # Extraire les valeurs d'intensité
            intensity_values = df['Intensity [arb. units]'].values

            # Ajouter les valeurs d'intensité à la liste
            self.intensity_data.append(intensity_values)

        # Créer une matrice numpy à partir des valeurs d'intensité
        self.intensity_matrix = np.array(self.intensity_data)

        # Transposer la matrice pour avoir les wavenumbers en colonne et les valeurs d'intensité en ligne
        self.intensity_matrix = self.intensity_matrix.T

        # Créer un heatmap à partir de la matrice d'intensité
        self.fig = plt.figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('FROSt Trace')
        sns.heatmap(self.intensity_matrix, cmap='viridis', cbar_kws={'label': 'Intensity'}, ax=self.ax)

        # Masquer les index de l'axe des ordonnées
        self.ax.set_yticks([])

        # Créer le canevas pour afficher le graphique dans la GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack()

        # Ajouter un bouton pour enregistrer le graphique
        self.save_button = Button(self.master, text="Enregistrer", command=self.save_plot)
        self.save_button.pack(side="bottom", pady=10)

    def get_latest_directory(self, base_directory):
        # Obtenir une liste de tous les sous-dossiers dans le répertoire de base
        subdirs = [os.path.join(base_directory, d) for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
        # Trier les sous-dossiers par date de création
        subdirs.sort(key=os.path.getctime, reverse=True)
        # Retourner le dernier dossier créé (le plus récent)
        return subdirs[0] if subdirs else None

    def save_plot(self):
        # Demander à l'utilisateur de choisir un fichier pour enregistrer le graphique
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"),
                                                            ("All files", "*.*")])
        if file_path:
            # Sauvegarder les données de la matrice d'intensité dans un fichier texte
            np.savetxt(file_path, self.intensity_matrix, delimiter=',', header='Intensity Matrix')

def main():
    root = Tk()
    app = HeatmapGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
