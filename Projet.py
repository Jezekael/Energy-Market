#-*-coding:utf-8-*

import threading as th
import multiprocessing as ms
import signal
import queue
import sys
import time
import random
import math
from meteo import meteo
from marche import marche, empty_queue
from maison import maison

#shared memory : 0: T à t-1 1: T à t 2: Small disaster 3: huge disaster
def defInt(var,question):
    entre=input(question)
    while(var==0):
        if entre.isdigit():
            var=int(entre)
            return var
        else:
            entre=input("Entrez une valeur numerique svp ")

if __name__ == "__main__":

    try :
        #nombre de jour et de maison
        nombre_jours=0
        nombre_jours=defInt(nombre_jours, "Combien de jours de simulation ? ")

        nombre_maisons=0
        nombre_maisons=defInt(nombre_maisons, "Combien de maisons dans la simulation ? ")

        pause=0
        pause= defInt(pause,"Une pause de combien de secondes entre chaque journée ? ")


        print("C'est parti !!!!!!!!!!!!!!!!!!!")
        print("")
        print("")
        print("")

        print("███████╗███╗   ██╗███████╗██████╗  ██████╗██╗   ██╗    ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗")
        print("██╔════╝████╗  ██║██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝    ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝")
        print("█████╗  ██╔██╗ ██║█████╗  ██████╔╝██║  ███╗╚████╔╝     ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║   ")
        print("██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║ ╚██╔╝      ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║   ")
        print("███████╗██║ ╚████║███████╗██║  ██║╚██████╔╝  ██║       ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║   ")
        print("╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ")
        print("                                                                                                           ")
        
        memoire_partagee = ms.Array('f',10)

        #Initialisation des facteurs métérologiques
        facteur_meterolique = [25, 10, 4, 500] #CHANGEMENT *****************************************************************
         #coeff = [Température, Vent, Soleil, Pluie]
        coeffs_meterolique = [0.01,0.01,0.02,0.01]

        nombre_thread = 10

        
        barriere_maison = ms.Barrier(nombre_maisons)
        barriere_marche = ms.Barrier(nombre_maisons+1)
        barriere_meteo = ms.Barrier(nombre_maisons+1)
        jour = ms.Barrier(nombre_maisons+2)

        cadenas = ms.Lock()
        


        #coeff = [marchée, manifestations, réglementations énergetiques, penurie de charbon, penurie de fuel, mauvaise note, Macron, gilets jaune]
        coeffs = [0.1,0.022,0.124,0.118,0.121,0.12,0.009,0.127]
        probas = [math.pow(10,-2),math.pow(10,-3),math.pow(10,-2),math.pow(10,-2),math.pow(10,-3),math.pow(10,-4),math.pow(10,-3)]

        #Creation les listes de queues partagées pour Maison et Marchée
        maison_don_queue = ms.Queue(nombre_maisons)
        maison_prendre_queue = ms.Queue(nombre_maisons)
        marche_maison = ms.Queue(nombre_maisons)

        #Création des processus
        meteo_process = meteo(memoire_partagee, jour, nombre_jours, facteur_meterolique)
        marche_process = marche(memoire_partagee, coeffs, coeffs_meterolique, probas, marche_maison, jour, barriere_marche, barriere_meteo, cadenas, nombre_jours, nombre_thread, pause)
        maisons_processus = [maison(i+1, memoire_partagee, maison_don_queue, maison_prendre_queue, marche_maison, jour, barriere_maison, barriere_marche, barriere_meteo, cadenas, nombre_jours) for i in range (nombre_maisons)]

        #Début des processus
        meteo_process.start()
        marche_process.start()
        for processus in maisons_processus :
            processus.start()

        #Rejoindre les processus
        meteo_process.join()
        marche_process.join()
        for processus in maisons_processus :
            processus.join()

        #Fin des processus
        meteo_process.terminate()
        marche_process.terminate()
        for processus in maisons_processus :
            processus.terminate()
    
    #Gestions de Ctrl-c pour interrompre programme
    except KeyboardInterrupt:
        meteo_process.terminate()
        marche_process.terminate()
        for processus in maisons_processus :
            processus.terminate()

    print("Fin de la simulation")
