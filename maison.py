import multiprocessing as ms
import random
from marche import empty_queue

class maison(ms.Process):
    
    def __init__(self, nombre, memoire_partagee, maison_don_queue, maison_prendre_queue,marche_maison,jour,barriere_maison,barriere_marche, barriere_meteo, cadenas, nombre_jours):
        super().__init__()
        self.nombre = nombre
        self.production = random.random()
        self.consommation = random.random()
        self.politique_echange = random.randint(0,2)
        self.quantite_energie = self.production - self.consommation
        self.memoire_partagee = memoire_partagee
        self.maison_don_queue = maison_don_queue
        self.maison_prendre_queue = maison_prendre_queue
        self.cadenas = cadenas
        self.barriere_maison = barriere_maison
        self.marche_maison = marche_maison
        self.barriere_marche = barriere_marche
        self.barriere_meteo = barriere_meteo
        self.jour = jour
        self.nombre_jours = nombre_jours



    def run(self):
    
        jour=1
        while jour<=self.nombre_jours:
            
            #Attente du processus réseau
            self.jour.wait()
            self.barriere_meteo.wait()
            jour+=1

            #Mise à jour de la consommation 
            self.consommation = self.consommation * (self.memoire_partagee[1]-25)
            
            if self.consommation >= 1.0 :
                self.consommation = 0.99999
            if self.consommation < 0.0 :
                self.consommation = 0.0
            
            #Quantité d'énergie calculé
            self.quantite_energie = self.production - self.consommation

            #Surplus d'énergie et poilitique d'échange "échanger"
            if self.quantite_energie > 0.0 and self.politique_echange != 0 :
                
                self.deposer()
                
                self.barriere_maison.wait()
                self.maison(self.quantite_energie, " propose "+ str(round(self.quantite_energie,2))+" d'énergie gratuitement.")
                self.barriere_maison.wait()

                self.verifier_don()

                if self.quantite_energie > 0.0  and self.politique_echange == 2:
                    self.vendre()
                    self.maison(0, " a vendu " + str(round(self.quantite_energie,2))+ " d'énergie au marché.")
                    self.quantite_energie = 0.0
                
                elif self.quantite_energie > 0.0 and self.politique_echange == 1 :
                    self.maison(0, " jette "+ str(round(self.quantite_energie,3))+ " d'énergie.")
                    self.quantite_energie = 0.0
                    
            #Surplus d'énergie et poilitique d'échange "toujours vendre"
            if self.quantite_energie > 0.0 and self.politique_echange == 0 :
                self.vendre()
                self.maison(0, " a directement vendu "+ str(round(self.quantite_energie,3))+" d'énergie au marché.")
                self.quantite_energie = 0.0
                self.barriere_maison.wait()
                self.barriere_maison.wait()

            #Manque d'energie
            elif self.quantite_energie<0.0 :
                self.maison(self.quantite_energie, " est en manque d'énergie.")
                self.barriere_maison.wait()
                self.cadenas.acquire()
                for _ in range(self.maison_don_queue.qsize()) :
                    amount = self.maison_don_queue.get()
                    if self.quantite_energie + amount >= 0.0 and not self.maison_prendre_queue.full():
                        self.maison_prendre_queue.put(amount)
                        self.quantite_energie = 0.0
                        self.maison(self.quantite_energie, "a pris "+ str(round(amount,3))+" d'énergie gratuitement")
                        break
                    else :
                        self.maison_don_queue.put(amount)
                if self.quantite_energie < 0.0 :
                    self.marche_maison.put(self.quantite_energie)
                    self.maison(0, " a acheté "+ str(round(self.quantite_energie,3))+" d'énergie au marché.")
                    self.quantite_energie = 0.0
                self.cadenas.release()
                self.barriere_maison.wait()

            #permet au marché de commencer et d'attendre la fin de jorunée
            self.barriere_marche.wait()
            self.jour.wait()
            if self.nombre == 1 :
                empty_queue(self.maison_don_queue)
                empty_queue(self.maison_prendre_queue)

    def deposer(self) :
        self.cadenas.acquire()
        self.maison_don_queue.put(self.quantite_energie)
        self.cadenas.release()

    def verifier_don(self) :
        self.cadenas.acquire()
        if not self.maison_prendre_queue.empty() :
            for _ in range(self.maison_prendre_queue.qsize()) :
                amount2 = self.maison_prendre_queue.get()
                if amount2 == self.quantite_energie :
                    self.maison(0, ' a donné '+ str(round(self.quantite_energie,3))+" d'énergie gratuitement.")
                    self.quantite_energie = 0.0
                    break
                else:
                    self.maison_prendre_queue.put(amount2)
        self.cadenas.release()

    def vendre(self) :
        self.cadenas.acquire()
        self.marche_maison.put(self.quantite_energie)
        self.cadenas.release()

    def maison(self, energy, s) :
        a=round(self.production,2)
        b=round(self.consommation,2)
        c=round(energy, 5)
        print("Maison n°",self.nombre,' ',self.afficher_politique(self.politique_echange), s, sep="")

    def afficher_politique(self, p):
        return {
            0: "avec une poilitique d'échange 'toujours vendre'",
            1: "avec une poilitique d'échange 'toujours acheter'",
            2: "avec une poilitique d'échange 'vendre si pas de preneurs'",
        }[p]