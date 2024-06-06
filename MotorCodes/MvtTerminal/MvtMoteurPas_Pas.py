"""
Script: MvtMoteurPas_Pas.py
Author: Enzo Sebiane
GitHub: https://github.com/Enzo77360
Date: 2024-05-22
Description: This script controls a motor using Thorlabs Motion Control libraries.
"""

import clr
import sys
from System import Decimal, Int32
import time

# Importer les bibliothèques Kinesis
dll_path = r'C:\\Program Files\\Thorlabs\\Kinesis'
if dll_path not in sys.path:
    sys.path.append(dll_path)

clr.AddReference('Thorlabs.MotionControl.DeviceManagerCLI')
clr.AddReference('Thorlabs.MotionControl.KCube.DCServoCLI')
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI

class MotorController:
    def __init__(self):
        # Initialiser le gestionnaire de périphériques
        DeviceManagerCLI.BuildDeviceList()
        self.device_list = DeviceManagerCLI.GetDeviceList()
        self.device_list_python = [str(device) for device in self.device_list]

    def connect_motor(self):
        print("Périphériques détectés:", self.device_list_python)
        device_id = input("Entrez l'ID du périphérique : ")
        if device_id not in self.device_list_python:
            raise Exception(f"Le périphérique avec l'ID {device_id} n'est pas détecté.")
        self.motor = KCubeDCServo.CreateKCubeDCServo(device_id)
        self.motor.Connect(device_id)
        print('Initialisation du moteur...')
        self.motor.LoadMotorConfiguration(device_id)
        self.motor.StartPolling(250)
        self.motor.EnableDevice()
        self.motor.Home(60000)

    def move_motor(self, step_distance, total_steps, time_breaker):
        for position in range(total_steps + 1):
            target_position = Decimal(position) * step_distance
            self.motor.MoveTo(target_position, Int32(3000))
            time.sleep(time_breaker)

    def disconnect_motor(self):
        self.motor.StopPolling()
        self.motor.Disconnect()
        print("Mouvements terminés.")

def main():
    controller = MotorController()
    controller.connect_motor()
    step_distance = Decimal(float(input("Entrez la distance de chaque pas de la vis du moteur (1.0 = 1 mm) : ")))
    total_steps = int(input("Entrez le nombre de pas (entier) : "))
    time_breaker = int(input("Entrez le temps de pause des pas (en s) : "))
    controller.move_motor(step_distance, total_steps, time_breaker)
    controller.disconnect_motor()

if __name__ == "__main__":
    main()
