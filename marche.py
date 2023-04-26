import multiprocessing as ms
from multiprocessing import Process
import signal
import random
import threading as th
import queue
import os
import time
import numpy as np
import matplotlib.pyplot as plt

class marche(ms.Process):

    def __init__ (self, memoire_partagee, coeff, coeffs_meterolique, proba, marche_maison, jour, barriere_marche, barriere_meteo, cadenas, nombre_jours, nombre_thread, pause):
        super().__init__()
        self.coeff = coeff
        self.coeffs_meterolique = coeffs_meterolique
        self.memoire_partagee = memoire_partagee
        self.evenement = [0,0,0,0,0,0,0,0]
        self.signaux = [1,2,3,4,5,6,7]
        self.prix_energie = 100.0
        self.energie_entrante = 0.0
        self.energie_sortante = 0.0
        self.long_duree_coeff = 0.995
        self.resut_trans = 0
        self.proba = proba
        self.barriere_marche = barriere_marche
        self.barriere_meteo = barriere_meteo
        self.marche_maison = marche_maison
        self.cadenas = cadenas
        self.jour = jour
        self.compteur_jour = 0
        self.nombre_jours = nombre_jours
        self.nombre_thread = nombre_thread
        self.evenement_clee = []
        self.pause = pause

    def run(self):
        moyenne_meteo = self.coeffs_meterolique
        prix = []
        
        for i in self.signaux :
            signal.signal(i,self.gestionnaire_evenement)
        self.compteur_jour=1

        while self.compteur_jour<=self.nombre_jours:
            time.sleep(self.pause)
            print("############## Jour ", self.compteur_jour," ##############" ) 
                     
            eco_pol = ms.Process(target=self.externe, args=())
            eco_pol.start()
            eco_pol.join()
            eco_pol.terminate()
            
            
            #Attend le processus météo
            self.jour.wait()
            print("\n(Température : ", round(self.memoire_partagee[0], 1),"°C)\n(vent : ", round(self.memoire_partagee[1], 0),"km/h)\n(Soleil: ", round(self.memoire_partagee[2],0),"h par jour)\n(Pluie : ", round(self.memoire_partagee[0], 2),"mm)\n" )
            self.barriere_meteo.wait()
            
            impact_meterologique = 0
            for i in range(4) :
                impact_meterologique += ((float(self.memoire_partagee[i])-moyenne_meteo[i]))*self.coeffs_meterolique[i]
            
            impact_evenement = 0    
            for i in range(1, len(self.evenement)) :
                impact_evenement += self.coeff[i]*self.evenement[i]
                
            #Attend la barrière
            self.barriere_marche.wait()

            while True :
                self.cadenas.acquire()
                a = self.marche_maison.empty()
                self.cadenas.release()

                if a == True :
                    break

                else :

                    threads = [th.Thread(target=self.transaction, args=(self.marche_maison, self.cadenas)) for i in range(self.nombre_thread)]

                    for thread in threads:
                        thread.start()
       
                    for thread in threads:
                        thread.join()

            if self.prix_energie >= 300 :
                self.prix_energie = 300
            elif self.prix_energie <= 100 :
                self.prix_energie = 100

            #Evaluation du cours de l'energie
            self.prix_energie = self.prix_energie*self.long_duree_coeff + impact_evenement + impact_meterologique + self.resut_trans * (-self.coeff[0]) 

            prix.append(self.prix_energie)
            print("Prix de l'énergie: ", self.prix_energie, "€\n")
            self.compteur_jour+=1

            empty_queue(self.marche_maison)
            self.jour.wait()

        fig, ax = plt.subplots()
        ax.plot(prix)

        ax.set_xlabel('Jours')
        ax.set_ylabel('Prix')
        ax.set_title("Evolution du prix de l'énergie sur les "+ str(self.compteur_jour-1) +' derniers jours')

        # Plot les évenements clées sur le graphe
        for evenement in self.evenement_clee:
            ax.scatter(evenement[0], evenement[1], color='red', s=50)

        # Montre le graphe
        plt.show()

    #gestionnaire des signaux
    
    def gestionnaire_evenement(self, sig, frame):
            self.evenement[sig] = 1
            self.evenement_clee.append([self.compteur_jour, self.prix_energie])
            print("\nNEWS:", self.afficher_evenement(sig),"\n")

    def afficher_evenement(self, ev):
        return {
            0: "Une nouvelle marche pour le climat a été annoncer dans toute la France, les manifestants bloquent l'accès aux centrales nucléaires et charbons...",
            1: "Des rumeurs circulent à propos de nouvelles réglementations énergetiques gouvernementales favorisant la production d'énergie à faible coût!",
            2: "Il y'a une interruptions d'approvisionnement de charbons, les centrales ne fonctionnent plus!",
            3: "Une importante pénurie du fuel est ovbersable en France, les fluctuations des prix des carburants sont incontrolables!",
            4: "Les enseignant de TC on mis une mauvaise à un groupe d'étudiants qui n'ont pas attendu pour répandre l'incident sur les réseaux, entrainant de milliers de gens à tous casser dans la rue!",
            5: "Macron se trompe de boutton et publient ses nudes sur twitter, étrangement le public est plutôt favorable mais l'angoument énorme sur les réseaux creer une demande accrue d'énergie aux serveurs de Twitter!",
            6: "Un gilets jaunes s'est rendu compte ques les pages jaunes étaient fabriquées à partir d'abres, l'entiereté du mouvement s'est reconverti en secte écologique, la consomation d'énérgie nationale baisse grandement..."
        }[ev-1]


    def transaction(self, q, cadenas):
        cadenas.acquire()
        try :
            val = q.get(False)
            self.resut_trans = self.resut_trans + val
            print("Transaction effectuée de", round(val, 2), "énergie.")
        except queue.Empty:
            pass
        cadenas.release()
    
    def externe(self):
        for i in range(len(self.proba)) :
            if (random.randint(1,int(1/self.proba[i])))==1 :
                 os.kill(os.getppid(), self.signaux[i])

def empty_queue(q):
    while not q.empty():
        _ = q.get()