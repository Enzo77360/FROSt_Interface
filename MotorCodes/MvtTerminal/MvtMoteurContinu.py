"""
Fichier: MvtMoteurContinu.py
Créé par: Enzo Sebiane
GitHub: https://github.com/Enzo77360
Date de création: 22 mai 2024
Description: Ce programme se connecte à un périphérique KCubeDCServo, configure le mouvement du moteur,
             effectue le déplacement, attend la fin du mouvement, puis déconnecte le périphérique.
"""
import clr
import os
import sys
import time
from System import Decimal, Int32
import ctypes

# Importer les bibliothèques Kinesis
dll_path = r'C:\Program Files\Thorlabs\Kinesis'
if dll_path not in sys.path:
    sys.path.append(dll_path)

clr.AddReference('Thorlabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.KCube.DCServoCLI')
clr.AddReference('Thorlabs.MotionControl.GenericMotorCLI')

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo
from Thorlabs.MotionControl.GenericMotorCLI import MotorDirection
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import VelocityParameters
class KCubeDCServoController:
    def __init__(self):
        # Initialiser le gestionnaire de périphériques
        DeviceManagerCLI.BuildDeviceList()

        # Obtenir la liste des périphériques
        self.device_list = DeviceManagerCLI.GetDeviceList()

        # Convertir la liste en liste Python pour un affichage correct
        self.device_list_python = [str(device) for device in self.device_list]

        # Initialiser l'ID du périphérique à None
        self.device_id = None

    def connect_motor(self):
        print("Périphériques détectés:", self.device_list_python)

        if self.device_id == None:
            # Demander à l'utilisateur l'ID du périphérique
            self.device_id = input("Entrez l'ID du périphérique : ")

        # Vérifier que le périphérique est détecté
        if self.device_id not in self.device_list_python:
            raise Exception(f"Le périphérique avec l'ID {self.device_id} n'est pas détecté.")

        # Connecter au périphérique
        self.motor = KCubeDCServo.CreateKCubeDCServo(self.device_id)
        self.motor.Connect(self.device_id)

        # Initialiser le moteur
        print('Initialisation du moteur...')
        self.motor.LoadMotorConfiguration(self.device_id)
        self.motor.StartPolling(250)
        self.motor.EnableDevice()
        self.motor.Home(60000)  # Temporisation de 60 secondes pour l'opération de homing

    def configure_movement(self):
        # Demander à l'utilisateur les paramètres du mouvement
        distance_total_mm = float(input("Entrez la distance totale à parcourir (en mm) : "))
        temps_total_s = float(input("Entrez le temps total pour le déplacement (en secondes) : "))
        # Calculer la vitesse en mm/s
        vitesse_mm_s = distance_total_mm / temps_total_s

        # Convertir en Decimal pour les opérations
        distance_total = Decimal(distance_total_mm)
        temps_total = Decimal(temps_total_s)

        # Calculer la vitesse en mm/s
        self.vitesse = Decimal(vitesse_mm_s)

        # Configurer les paramètres de vitesse
        velocity_params = self.motor.GetVelocityParams()
        velocity_params.MaxVelocity = self.vitesse
        self.motor.SetVelocityParams(velocity_params)

        self.distance_total = distance_total
        self.temps_total_s = temps_total_s

    def move_motor(self):
        # Démarrer le mouvement
        print(f'Déplacement de {self.distance_total} mm à une vitesse de {self.vitesse} mm/s')
        self.motor.MoveTo(self.distance_total, Int32(60000))

    def wait_for_completion(self):
        # Attendre la fin du mouvement
        time.sleep(self.temps_total_s + 1)  # On attend légèrement plus que le temps total pour être sûr que le mouvement soit terminé

    def disconnect_motor(self):
        # Déconnecter le périphérique
        self.motor.StopPolling()
        self.motor.Disconnect()
        print("Mouvements terminés.")

def main():
    controller = KCubeDCServoController()
    controller.connect_motor()
    controller.configure_movement()
    controller.move_motor()
    controller.wait_for_completion()
    controller.disconnect_motor()

if __name__ == "__main__":
    main()