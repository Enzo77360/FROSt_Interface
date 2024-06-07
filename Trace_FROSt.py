import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import numpy as np

# Chemin du dossier contenant les fichiers CSV
directory = "Acquisitions"

# Liste des fichiers CSV dans le dossier
files = glob.glob(directory + '/*.csv')

# Initialiser une liste pour stocker les valeurs d'intensité de chaque fichier
intensity_data = []

# Parcourir chaque fichier CSV dans la liste et extraire les valeurs d'intensité
for file in files:
    # Lire le fichier CSV en tant que DataFrame pandas
    df = pd.read_csv(file)

    # Extraire les valeurs d'intensité
    intensity_values = df['Intensity [arb. units]'].values

    # Ajouter les valeurs d'intensité à la liste
    intensity_data.append(intensity_values)

# Créer une matrice numpy à partir des valeurs d'intensité
intensity_matrix = np.array(intensity_data)

# Transposer la matrice pour avoir les wavenumbers en colonne et les valeurs d'intensité en ligne
intensity_matrix = intensity_matrix.T

# Créer un heatmap à partir de la matrice d'intensité
plt.figure(figsize=(10, 6))
sns.heatmap(intensity_matrix, cmap='viridis', cbar_kws={'label': 'Intensity'})

# Étiqueter les axes
plt.ylabel('Wavenumber [cm^-1]')
plt.xlabel('Index de la ligne')

# Titre du graphique
plt.title('Heatmap de l\'intensité en fonction du wavenumber pour chaque fichier')

# Afficher le graphique
plt.tight_layout()
plt.show()
