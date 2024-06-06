import clr  # package pythonnet
import os
import sys
from System import Decimal, Int32  # Importer Decimal de System

# Ajouter le chemin vers les DLLs de Kinesis
dll_path = r'C:\\Program Files\\Thorlabs\\Kinesis'
if dll_path not in sys.path:
    sys.path.append(dll_path)

# Charger les DLLs nécessaires
clr.AddReference('Thorlabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.GenericMotorCLI')
clr.AddReference('Thorlabs.MotionControl.KCube.DCServoCLI')

# Importer les namespaces nécessaires
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo

# Initialiser le gestionnaire de périphériques
DeviceManagerCLI.BuildDeviceList()

# Obtenir la liste des périphériques
device_list = DeviceManagerCLI.GetDeviceList()

# Convertir la liste en liste Python pour un affichage correct
device_list_python = [str(device) for device in device_list]

print("Périphériques détectés:", device_list_python)

# Définir l'ID du périphérique
device_id = '27260229'

# Vérifiez que le périphérique est détecté
if device_id not in device_list_python:
    raise Exception(f"Le périphérique avec le numéro de série {device_id} n'est pas détecté.")

# Connecter au périphérique
motor = KCubeDCServo.CreateKCubeDCServo(device_id)
motor.Connect(device_id)

# Initialiser le moteur
motor.LoadMotorConfiguration(device_id)
motor.StartPolling(250)
motor.EnableDevice()
motor.Home(60000)  # Temporisation de 60 secondes pour l'opération de homing

# Déplacer le moteur à une position spécifique
position = Decimal(2.0)  # Utiliser System.Decimal pour la position
timeout = Int32(60000)  # Temporisation de 60 secondes convertie en Int32
motor.MoveTo(position, timeout)  # Utiliser les types corrects pour les arguments

# Déconnecter le périphérique
motor.StopPolling()
motor.Disconnect()

print("Mouvement terminé.")
