# MoteurThorlabsKinesis

Repository créé par Enzo Sebiane pour le contrôle des moteurs Thorlabs à l'aide de l'API Kinesis.

## Auteurs

- Enzo Sebiane

## Contenu

Ce repository contient les scripts Python pour contrôler les moteurs Thorlabs à l'aide de l'API Kinesis.

### Codes Principaux

1. **MoteurMvtContinu.py**
   - Ce script permet de contrôler le mouvement continu du moteur en spécifiant une vitesse et une direction.

2. **MvtMoteurPas_Pas.py**
   - Ce script permet de contrôler le mouvement du moteur pas à pas en spécifiant la distance de chaque pas, le nombre total de pas, et le temps de pause entre chaque pas.

## Prérequis

- Python 3.x
- Bibliothèques Python : `clr`, `System`, `Thorlabs.MotionControl.DeviceManagerCLI`, `Thorlabs.MotionControl.KCube.DCServoCLI`

## Utilisation

1. Assurez-vous d'avoir installé Python 3.x sur votre système.
2. Installez les bibliothèques requises en exécutant `pip install clr`.
3. Téléchargez et installez les pilotes Thorlabs Kinesis sur votre système.
4. Exécutez les scripts Python dans le dossier `codespy` pour contrôler les moteurs Thorlabs.

## Licence

 - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.

