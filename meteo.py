import multiprocessing as ms 
import random

class meteo(ms.Process):

    def __init__(self, memoire_partagee, jour, nombre_jours, facteur_meterolique):
        super().__init__()
        self.facteur_meterolique = facteur_meterolique
        self.memoire_partagee = memoire_partagee
        self.jour = jour
        self.nombre_jours = nombre_jours

    def run(self):

        #Add inital temperature
        for i in range(4) :
            self.memoire_partagee[i] = self.facteur_meterolique[i]
        jour=1
        while jour<= self.nombre_jours : 

            jour += 1

            #Actualise la nouvelle temperature
            self.facteur_meterolique[0] += random.normalvariate(0, 2)
            if self.facteur_meterolique[0] >= 40 :
                self.facteur_meterolique[0] = 35
            elif self.facteur_meterolique[0] <= -10 :
                self.facteur_meterolique[0] = -5
            
            #Actualise le nouveau facteur vent (varie entre 0 et 70 km/h, en moyenne 15 km/h)
            self.facteur_meterolique[1] = abs(random.normalvariate(0, 15))
            if self.facteur_meterolique[0] >= 70 :
                self.facteur_meterolique[0] = 70

            #Actualise le nouveau facteur soleil (varie entre 0 et 24 h de soleil par jour, en moyenne 4h)
            self.facteur_meterolique[2] = abs(random.normalvariate(0, 4))
            if self.facteur_meterolique[0] >= 24 :
                self.facteur_meterolique[0] = 24

            #Actualise le volume de précipitations (varie entre 0 et 2000 millimètres, en moyenne 1000 mm)
            self.facteur_meterolique[3] = random.randint(0, 2000)


            #Stock les facteurs métérologiques dans la mémoire partagée
            for i in range(4) :
                self.memoire_partagee[i] = self.facteur_meterolique[i]

            #Pemert aux processus d'attendre la fin de journée
            self.jour.wait()
            self.jour.wait()