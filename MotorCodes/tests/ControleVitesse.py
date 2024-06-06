import clr  # package pythonnet
import os
import sys
import time
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

# Boucle pour déplacer progressivement le moteur
for position in range(3):  # De 0 à 5 inclus
    motor.MoveTo(Decimal(position), Int32(3000))  # Déplacer le moteur à la position avec un timeout de 3 secondes
    time.sleep(1)  # Attendre 3 secondes avant le prochain mouvement

# Déconnecter le périphérique
motor.StopPolling()
motor.Disconnect()

print("Mouvements terminés.")
