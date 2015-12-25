# -*-coding:utf-8-*-
__author__ = 'Clément'

import argparse
import os
import platform
import re
import sqlite3
import threading
from gestion_courriel.Gmail import *
from gestion_courriel.extraire_xml import extraire_question, extraire_ordre
from oauth2client.tools import argparser
from serial import Serial, SerialException

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arrosage_automatique.settings")
from gestion_temps import *
from gestion_arrosage_automatique.models import ConditionsMeteorologiques, ConditionArrosage


# port_serie = Serial(port = PORT, baudrate = 9600)

def trouver_ports_libres():
    available = []
    for i in range(256):
        try:
            s = Serial(i)
            available.append((i, s.portstr))
            s.close()
        except:
            continue
    print available


class RecuperateurDonnees:
    def __init__(self, chemin_base_donnee):
        assert isinstance(chemin_base_donnee, str)
        self.chemin_base_donnee = chemin_base_donnee
    def enregistrer_courriel(self, emetteur, recepteur, objet, texte):
        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
            INSERT INTO Courriel(emetteur, recepteur, objet, texte)
            VALUES (?,?,?,?);
            """, (emetteur, recepteur, objet, texte))
        connex.close()
    def obtenir_conditions_meteorologiques_depuis(self, jours):
        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
        SELECT *
        FROM ConditionsMeteorologiques
        """)
        connex.commit()
        #[compteur, date, temperature, humidite] = cursor.fetchone()
        res = cursor.fetchall()
        print res[0]
        res = [(i.temperature,i.humidite_relative, i.date) for i in res if datetime.timedelta.total_seconds(i.date - datetime.datetime.now()) < jours*86400]
        #res = []
        connex.close()
        return res

    def obtenir_conditions_meteorologiques(self):
        """
        Connexion à la base de données pour obtenir les derniers relevés de la situation météorologique
        :return:
        """

        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
        SELECT *
        FROM ConditionsMeteorologiques
        WHERE compteur IN  (SELECT max(compteur) FROM ConditionsMeteorologiques)
        """)

        connex.commit()
        [compteur, date, temperature, humidite] = cursor.fetchone()
        res = cursor.fetchone()
        connex.close()
        return res

    def enregistrer_arrosage(self, duree):
        """
        Remplit la table Arrosage à chaque fin d'arrosage
        :param duree : durée de l'arrosage
        :return:
        """
        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
        SELECT compteur
        FROM Arrosage
        WHERE compteur IN (SELECT max(compteur) FROM Arrosage)
        """)
        connex.commit()
        compteur = cursor.fetchone()
        cursor.execute("""
            INSERT INTO Arrosage(compteur, date_exacte, duree)
            VALUES (?,?,?);
            """, (str(compteur + 1), time.asctime(time.time()), str(duree)))
        connex.close()

    def obtenir_conditions_arrosage(self):
        """
        Consulte la base de donnée base_arrosage.db pour récupérer les données sur les
        moment adéquat pour arroser
        :return:
        """
        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
        SELECT *
        FROM ConditionArrosage
        WHERE compteur IN (SELECT max(compteur) FROM ConditionArrosage)
        """)

        connex.commit()
        # [compteur, temperature_min, humidite_max, frequence_min, heure_min, heure_max, duree ] = cursor.fetchone()
        res = cursor.fetchone()
        connex.close()
        return res

    def enregistrer_temperature(self, date_exacte, temperature, humidite):
        # fonction quasiment identique à enregistrer_humidite
        connex = sqlite3.connect("base_arrosage.db")
        cursor = connex.cursor()
        cursor.execute("""
        SELECT compteur
        FROM ConditionsMeteorologiques
        WHERE compteur IN (SELECT max(compteur) FROM ConditionsMeteorologiques)
        """)

        connex.commit()
        compteur = cursor.fetchone()
        connex.execute("""
         INSERT INTO ConditionsMeteorologiques(compteur, date_exacte, temperature, humidite_relative)
          VALUES (?,?,?);
           """, (str(compteur + 1), time.asctime(date_exacte), str(temperature), str(humidite)))
        connex.close()

    def enregistrer_humidite(self, date_exacte, temperature, humidite):
        connex = sqlite3.connect("base_arrosage.db")
        cursor = connex.cursor()
        cursor.execute("""
        SELECT id
        FROM ConditionsMeteorologiques
        WHERE id IN (SELECT max(id) FROM ConditionsMeteorologiques)
        """)

        connex.commit()
        compteur = cursor.fetchone()
        cursor.execute("""
             INSERT INTO ConditionsMeteorologiques(id, date_exacte, temperature, humidite_relative)
            VALUES (?,?,?);
            """, (str(id + 1), time.asctime(date_exacte), str(temperature), str(humidite) ))
        connex.close()

    def enregistrer_mesure(self, date_exacte, temperature, humidite):
        connex = sqlite3.connect(self.chemin_base_donnee)
        cursor = connex.cursor()
        cursor.execute("""
        SELECT id
        FROM ConditionsMeteorologiques
        WHERE id IN (SELECT max(id) FROM ConditionsMeteorologiques)
        """)
        connex.commit()
        compteur = cursor.fetchone()
        cursor.execute("""
            INSERT INTO ConditionsMeteorologiques(id, date_exacte, temperature, humidite_relative)
            VALUES (?,?,?);
            """, (str(compteur + 1), time.asctime(date_exacte), str(temperature), str(humidite) ))
        connex.close()

class GestionnaireGmail(threading.Thread):
    def __init__(self, json_file, PROVENANCE_SURE, DESTINATAIRES):
        print "on gère les courriels"
        threading.Thread.__init__(self)
        parser = argparse.ArgumentParser(parents=[argparser])
        self.flags = parser.parse_args()
        self.PROVENANCE_SURE = PROVENANCE_SURE
        self.json_file = json_file
        self.parser = argparse.ArgumentParser(parents=[argparser])
        self.gmail_lire = Gmail(self.flags, client_secret_file =self.json_file, oauth_scope = 'https://www.googleapis.com/auth/gmail.readonly')
        self.gmail_enovoyer = Gmail(self.flags, client_secret_file =self.json_file, oauth_scope = 'https://www.googleapis.com/auth/gmail.send')
        messages = self.gmail_lire.getMessagesList()
        if messages['messages']:
            self.l_id_courriels = [ msg['id'] for msg in messages['messages']]
            #= gmail.getMessageDetails(msg['id'])
        self.destinataires = DESTINATAIRES
        systeme = platform.system()
        self.rec = RecuperateurDonnees(os.getcwd())
        print "initialisation"
    def run(self):
        derniere_mise_a_jour = time.time()
        periode_mise_a_jour_gmail = 120
        six_jours = 518400
        trois_jours = 3*24*3600
        reinitialisation_gmail = time.time()
        maintenant = 0
        while True:
            #maintenant = time.time()
            if distance_seconde(maintenant,derniere_mise_a_jour) > periode_mise_a_jour_gmail:
                print "on vérifie les courriels reçus"
                messages = self.gmail_lire.getMessagesList()
                if messages['messages']:
                    l_id = [msg['id'] for msg in messages['messages'] if not msg['id'] in self.l_id_courriels ]
                    for id in l_id:
                        m = self.gmail_lire.getMessageDetails(id)
                        if m.getFrom() in self.PROVENANCE_SURE:
                            self.rec.enregistrer_courriel(self, m.getFrom(), m.getTo(), m.getSubject(),
                                                          m.getText(self.gmail_lire, 'me', id))
                            if m.getSubject() == "ordre":
                                l_instructions = extraire_ordre(m.getText(self.gmail_lire, "arrosage.b@gmail.com", id))
                                # for instruction in l_instructions:
                                #     if instruction['categorie']
                                #     RecuperateurDonnees.obtenir_conditions_meteorologiques()
                            elif m.getSubject() == "questions":
                                l_instructions = extraire_question(m.getText(self.gmail_lire, "arrosage.b@gmail.com", id))
                            else:
                                pass


                            #TODO ici on vérifie qui envoie, et on interprète le resultat et on renvoie ce qu'il faut

                derniere_mise_a_jour = maintenant
            elif distance_jour(maintenant, reinitialisation_gmail) > 6:
                print "on réinitialise la connexion"
                self.gmail_lire = Gmail(self.flags, client_secret_file = self.json_file, oauth_scope = 'https://www.googleapis.com/auth/gmail.readonly')
                self.gmail_enovoyer = Gmail(self.flags, client_secret_file = self.json_file, oauth_scope = 'https://www.googleapis.com/auth/gmail.send')
                reinitialisation_gmail = maintenant
            elif distance_jour(maintenant, reinitialisation_gmail) > 3:
                print "on envoie un courriel à tout le monde"
                for destinataire in self.destinataires:

                    print self.rec.obtenir_conditions_meteorologiques()
                    #res = [(i.temperature,i.humidite_relative, i.date) for i in ConditionsMeteorologiques.objects.all() if datetime.timedelta.total_seconds(i.date - datetime.datetime.now())]
                    self.rec.obtenir_conditions_meteorologiques_depuis(3)
                    message = Message_Attachment(sender="arrosage.b@gmail.com",to=destinataire,subject="rapport météo",
                                                 message_text= "test", service=gmail.gmail_service)
                    #message = Message_Attachment(sender="arrosage.b@gmail.com",to=destinataire,subject="rapport météo",
                    #                             message_text= "test", file_dir=os.getcwd(), filename= "",
                    #                             service=gmail.gmail_service)
                    message.sendMessage(self.gmail_enovoyer, "arrosage.b@gmail.com")



class Decideur(threading.Thread):
    def __init__(self, lePort):
        threading.Thread.__init__(self)
        self.commu = Communication_Arduino(lePort)
    def run(self):
        """
        Méthode principale, là où tout se passe.
        :return:
        """
        derniere_mise_a_jour = time.time()
        derniere_prise_mesure = time.time()
        temps_dernier_arrosage = 0

        en_train_d_arroser = False
        debut_reelle_arrosage = False

        derniere_condo_meteo = ConditionsMeteorologiques.objects.get(
            id=max([i.id for i in ConditionsMeteorologiques.objects.all()]))
        print derniere_condo_meteo
        temperature = derniere_condo_meteo.temperature
        humidite = derniere_condo_meteo.humidite_relative

        derniere_condo_arrosage = ConditionArrosage.objects.get(id=max([i.id for i in ConditionArrosage.objects.all()]))
        print derniere_condo_arrosage
        temperature_min = derniere_condo_arrosage.temperature_min
        humidite_max = derniere_condo_arrosage.humidite_max
        frequence_min = derniere_condo_arrosage.frequence_min
        heure_min = derniere_condo_arrosage.heure_min
        heure_max = derniere_condo_arrosage.heure_max
        duree_arrosage_prevue = derniere_condo_arrosage.duree

        while True:
            #print 'on vérifie'
            try:
                maintenant = time.time()
                # mise à jour des données toutes les 5 minutes
                """
                if distance_seconde(maintenant, derniere_mise_a_jour) > 300:
                    print "on fait la mise à jour des paramètres d'arrosage"
                    #se tient à jour des paramètres pour arroser
                    derniere_condo_arrosage = ConditionArrosage.objects.get(
                        id=max([i.id for i in ConditionArrosage.objects.all()]))
                    temperature_min = derniere_condo_arrosage.temperature_min
                    humidite_max = derniere_condo_arrosage.humidite_max
                    frequence_min = derniere_condo_arrosage.frequence_min
                    heure_min = derniere_condo_arrosage.heure_min
                    heure_max = derniere_condo_arrosage.heure_max
                    duree_arrosage_prevue = derniere_condo_arrosage.duree
                    derniere_mise_a_jour = maintenant

                if humidite < humidite_max and distance_jour(maintenant, temps_dernier_arrosage) > \
                        frequence_min and donner_heure(maintenant) > heure_min and donner_heure(maintenant) < heure_max:
                    #vérifie si les conditions pour arroser sont remplies, si oui, on arrose
                    print "on arrose"
                    self.commu.arroser()

                    temps_dernier_arrosage = time.time()
                    lu = self.commu.ecouter()
                    if lu == "pompe_allumee":
                        debut_reelle_arrosage = maintenant
                        en_train_d_arroser = True
                if distance_seconde(maintenant, debut_reelle_arrosage) > duree_arrosage_prevue and en_train_d_arroser:
                    print "on n'arrose plus"
                    #si la durée de l'arrosage est supérieure à la durée prévue, alors on éteint la pompe
                    self.commu.eteindre_arrosage()
                    lu = self.commu.ecouter()
                    if lu == "pompe_eteinte":
                        fin_reelle_arrosage = maintenant
                        en_train_d_arroser = False
                        duree_reelle_arrosage = distance_seconde(debut_reelle_arrosage, fin_reelle_arrosage)
                        Arrosage(duree=duree_reelle_arrosage).save()
                """

                print distance_seconde(maintenant, derniere_prise_mesure)
                if distance_seconde(maintenant, derniere_prise_mesure) > 5:
                    #demande la température et l'enregistre dans une base de donnée
                    self.commu.combien_temperature()
                    print "on mesure la température"
                    time.sleep(1)
                    lu = self.commu.ecouter()
                    print lu
                    if re.match(r"(RX : )[0-9].\.[0-9].", lu) is not None:
                        temperature = lu[5:] #TODO à remettre sans RX :
                        print temperature
                    elif re.match(r"[0-9].\.[0-9].", lu):
                        temperature = lu
                        print temperature
                    else:
                        print "mauvaise donnée"
                        temperature = 0
                        continue
                    self.commu.combien_humidite()
                    print "on mesure l'humidité"
                    time.sleep(1)
                    lu = self.commu.ecouter()
                    print lu
                    if re.match(r"(RX : )[0-9].\.[0-9].", lu) is not None:
                        humidite = lu[5:] #TODO à remettre sans RX :
                        print humidite
                    elif re.match(r"[0-9].\.[0-9].", lu):
                        humidite = lu
                        print humidite
                    else:
                        print "mauvaise donnée humidité"
                        humidite = 0
                        continue
                    #on met à jour la date de dernière mesure et la dernière mesure que si on a bien eu la température
                    ## et l'humidité
                    ConditionsMeteorologiques(temperature=temperature, humidite_relative=humidite).save()

                    derniere_prise_mesure = maintenant
                if distance_seconde(maintenant, derniere_prise_mesure) > 3600:
                    pass
                    #TODO problème de réception, il faut envoyer un courriel d'erreur !
                time.sleep(0.5)
            except SerialException:
                print "impossible d'accéder au port"
                break
            """
            except:
                print "rien du tout"
                self.commu.quitter()
                break
                """


class Communication_Arduino:
    def __init__(self, lePort):
        self.port = lePort
        try:
            self.port_serie = Serial(port=self.port, baudrate=9600, timeout=0)
            print self.port_serie.isOpen()
        except SerialException:
            print "port série introuvable"

    def combien_temperature(self):
        # combien_temperature
        self.port_serie.write("t")

    def combien_humidite(self):
        # combien_humidite
        self.port_serie.write("h")

    def arroser(self):
        # arroser
        self.port_serie.write("a")

    def eteindre_arrosage(self):
        # eteindre_arrosage
        self.port_serie.write("e")

    # def en_train_d_arroser(self):
    # self.port_serie.write("en_train_d_arroser")
    def ecouter(self):
        print "on lit"
        return self.port_serie.readline()

    def parler(self, a_envoyer):
        #raw_input("écrire ici")
        self.port_serie.write(a_envoyer)
        return a_envoyer

    def quitter(self):
        self.port_serie.close()

if __name__ == "__main__":

    if platform.system() == "Windows":
        PORT = "COM3"
    else:
        PORT = "/dev/ttyACM0"
    #try:
    dec = Decideur(PORT)
    json_file = os.path.join("gestion_courriel", "client_secret.json")
    print json_file
    PROVENANCE_SURE = ["clemsciences@gmail.com","arrosage.b@gmail.com", "cendrine.besnier37@gmail.com", "patrick.besnier37@gmail.com"]
    DESTINATAIRES = ["clemsciences@gmail.com", "patrick.besnier37@gmail.com", "cendrine.besnier37@gmail.com"]
    gest = GestionnaireGmail(json_file, PROVENANCE_SURE, DESTINATAIRES)
    dec.start()
    gest.start()
    #except SerialException:
    #    print "port manquant"
        #TODO envoyer un mail?

