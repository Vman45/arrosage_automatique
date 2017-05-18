# -*-coding:utf-8-*-
import numpy as np
import datetime
import matplotlib.pyplot as plt
import os
DIRECTORY = "/home/pi/arrosage_automatique/arrosage_automatique/static/images"
conversion_mois = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre",
                       "novembre", "decembre"]

conversion_jour = {"Mon" : "Lundi", "Tue" : "Mardi", "Wed" : "Mercredi", "Thu" : "Jeudi", "Fri" : "Vendredi",
                       "Sat" : "Samedi", "Sun" : "Dimanche"}

nombre_jour_par_mois = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def obtenir_courbe_temperature_jour(temps, temperatures):
    # jour en datetime.datetime.now()
    jour = temps[0]
    jour_semaine = jour.ctime()[:3]
    nf_min = "minima_temperature_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_minima_temperature = os.path.join(DIRECTORY, nf_min)
    #nom_minima_temperature = "minima_temperature_jour.png"
    temps_minima_par_heure = list(set([timme.hour for timme in temps]))
    temps_minima_par_heure.sort()
    minima_par_heure = [min([tempe for i, tempe in enumerate(temperatures) if temps[i].hour == heure]) for heure in temps_minima_par_heure]
    plt.title(u"Courbe de temperature du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0,24, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(temps_minima_par_heure, minima_par_heure, marker="*")
    plt.savefig(nom_minima_temperature)
    plt.close()

    nf_max = "maxima_temperature_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_maxima_temperature = os.path.join(DIRECTORY, nf_max)
    #nom_maxima_temperature = "maxima_temperature_jour.png"
    temps_maxima_par_heure = list(set([timme.hour for timme in temps]))
    temps_maxima_par_heure.sort()
    maxima_par_heure = [max([tempe for i, tempe in enumerate(temperatures) if temps[i].hour == heure and type(tempe) == float] ) for heure in temps_maxima_par_heure]
    plt.title(u"Courbe de temperature du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0,24, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(temps_maxima_par_heure, maxima_par_heure, marker="*")
    plt.savefig(nom_maxima_temperature)
    plt.close()

    nf_moy = "moyennes_temperature_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_moyennes_temperatures = os.path.join(DIRECTORY, nf_moy)
    #nom_moyennes_temperatures = "moyennes_temperature_jour.png"
    temps_moyennes_par_heure = list(set([timme.hour for timme in temps]))
    temps_moyennes_par_heure.sort()
    moyennes_par_heure = [np.mean([tempe for i, tempe in enumerate(temperatures) if temps[i].hour == heure and type(tempe) == float]) for heure in temps_moyennes_par_heure]
    plt.title(u"Courbe de temperature du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0,24, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(temps_moyennes_par_heure, moyennes_par_heure, marker="*")
    plt.savefig(nom_moyennes_temperatures)
    plt.close()
    return nf_min, nf_max, nf_moy


def obtenir_courbe_temperature_mois(temps, temperatures, annee, mois):
    # jour en datetime.datetime.now()
    print(type(temperatures[0]))
    jours = list(set([jour.day for jour in temps]))
    jours.sort()
    nf_min = "minima_temperature_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_minima_temperatures_mois = os.path.join(DIRECTORY, nf_min)
    minima_par_jour = [min([tempe for i, tempe in enumerate(temperatures) if temps[i].day == jour and type(tempe) == float]) for jour in jours]
    # a = [tempe for jour in jours for i, tempe in enumerate(temperatures) if temps[i].day == jour ]
    # for i in a:
    #    if type(i) != float:
    #        print(type(i))
    plt.axis([0,nombre_jour_par_mois[mois-1], -20, 40])
    plt.grid(True)
    plt.title(u"Temperature minimale en "+conversion_mois[mois-1]+" "+str(annee))
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(jours, minima_par_jour, marker="*")
    plt.savefig(nom_minima_temperatures_mois)
    plt.close()

    nf_max = "maxima_temperature_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_maxima_temperatures_mois = os.path.join(DIRECTORY, nf_max)



    maxima_par_jour = [max([tempe for i, tempe in enumerate(temperatures) if temps[i].day == jour and type(tempe) == float]) for jour in jours]

    plt.axis([0,nombre_jour_par_mois[mois-1], -20, 40])
    plt.grid(True)
    plt.title(u"Temperature maximale en "+conversion_mois[mois-1]+" "+str(annee))
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(jours, maxima_par_jour, marker="*")
    plt.savefig(nom_maxima_temperatures_mois)
    plt.close()

    nf_moy = "moyennes_temperature_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_moyennes_temperatures_mois = os.path.join(DIRECTORY, nf_moy)
    moyennes_par_jour = [np.mean([tempe for i, tempe in enumerate(temperatures) if temps[i].day == jour and type(tempe) == float]) for jour in jours]
    plt.axis([0, nombre_jour_par_mois[mois-1], -20, 40])
    plt.grid(True)
    plt.title(u"Temperature moyenne en "+conversion_mois[mois-1]+" "+str(annee))
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.plot(jours, moyennes_par_jour, marker="*")
    plt.savefig(nom_moyennes_temperatures_mois)
    plt.close()
    return nf_min, nf_max, nf_moy


def obtenir_courbe_temperature_annee(temps, temperatures, annee):
    # jour en datetime.datetime.now()
    nf_min = "nom_temperature_annee_minima"+str(annee)+".png"
    nom_minima = os.path.join(DIRECTORY, nf_min)
    mois_presents = list(set([timme.month for timme in temps]))
    mois_presents.sort()
    minima_mensuels = [min([tempe for j, tempe in enumerate(temperatures) if temps[j].month == i and type(tempe) == float]) for i in mois_presents]
    plt.axis([0,12, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.title(u"Courbe de temperature de l'annee "+str(annee)+".")
    plt.plot(mois_presents, minima_mensuels, marker="*")
    plt.savefig(nom_minima)
    plt.close()

    nf_max = "nom_temperature_annee_maxima"+str(annee)+".png"
    nom_maxima = os.path.join(DIRECTORY, nf_max)
    maxima_mensuels = [max([tempe for j, tempe in enumerate(temperatures) if temps[j].month == i and type(tempe) == float]) for i in mois_presents]
    plt.axis([0,12, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.title(u"Courbe de temperature de l'annee "+str(annee)+".")
    plt.plot(mois_presents, maxima_mensuels, marker="*")
    plt.savefig(nom_maxima)
    plt.close()

    nf_moy = "nom_temperature_annee_moyennes"+str(annee)+".png"
    nom_moyennes = os.path.join(DIRECTORY, nf_moy)
    moyennes_mensuels = [np.mean([tempe for j, tempe in enumerate(temperatures) if temps[j].month == i and type(tempe) == float]) for i in mois_presents]
    plt.axis([0,12, -20, 40])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"temperature en °C")
    plt.title(u"Courbe de temperature de l'annee "+str(annee)+".")
    plt.plot(mois_presents, moyennes_mensuels, marker="*")
    plt.savefig(nom_moyennes)
    plt.close()

    return nf_min, nf_max, nf_moy



def obtenir_courbe_humidite_jour(temps, humidites):
    # jour en datetime.datetime.now()
    jour = temps[0]
    jour_semaine = jour.ctime()[:3]
    nf_min = "minima_humidite_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_minima_humidite = os.path.join(DIRECTORY, nf_min)
    temps_minima_par_heure = list(set([timme.hour for timme in temps]))
    temps_minima_par_heure.sort()
    minima_par_heure = [min([humi for i, humi in enumerate(humidites) if temps[i].hour == heure]) for heure in temps_minima_par_heure]
    plt.title(u"Courbe d'humidite du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0, 24, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(temps_minima_par_heure, minima_par_heure, marker="*")
    plt.savefig(nom_minima_humidite)
    plt.close()

    nf_max = "maxima_humidite_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_maxima_humidite = os.path.join(DIRECTORY, nf_max)
    temps_maxima_par_heure = list(set([timme.hour for timme in temps]))
    temps_maxima_par_heure.sort()
    maxima_par_heure = [max([humi for i, humi in enumerate(humidites) if temps[i].hour == heure]) for heure in temps_maxima_par_heure]
    plt.title(u"Courbe d'humidite du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0, 24, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(temps_maxima_par_heure, maxima_par_heure, marker="*")
    plt.savefig(nom_maxima_humidite)
    plt.close()

    nf_moy = "moyennes_humidite_jour_"+str(jour.year)+"_"+str(jour.month)+"_"+str(jour.day)+".png"
    nom_moyennes_humidite = os.path.join(DIRECTORY, nf_moy)
    temps_moyennes_par_heure = list(set([timme.hour for timme in temps]))
    temps_moyennes_par_heure.sort()
    moyennes_par_heure = [np.mean([humi for i, humi in enumerate(humidites) if temps[i].hour == heure]) for heure in temps_moyennes_par_heure]
    plt.title(u"Courbe d'humidite du "+
              conversion_jour[jour_semaine]+" "+str(jour.day)+" "+conversion_mois[jour.month-1]+".")
    plt.axis([0, 24, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(temps_moyennes_par_heure, moyennes_par_heure, marker="*")
    plt.savefig(nom_moyennes_humidite)
    plt.close()
    return nf_min, nf_max, nf_moy


def obtenir_courbe_humidite_mois(temps, humidites, annee, mois):
    # jour en datetime.datetime.now()
    jours = list(set([jour.day for jour in temps]))
    jours.sort()
    nf_min = "minima_humidite_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_minima_humidites_mois = os.path.join(DIRECTORY, nf_min)
    minima_par_jour = [min([humi for i, humi in enumerate(humidites) if temps[i].day == jour]) for jour in jours]
    plt.axis([0, nombre_jour_par_mois[mois-1], 0, 100])
    plt.grid(True)
    plt.title(u"Humidite minimale en "+conversion_mois[mois-1]+" "+str(annee)+".")
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(jours, minima_par_jour, marker="*")
    plt.savefig(nom_minima_humidites_mois)
    plt.close()

    nf_max = "maxima_humidite_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_maxima_humidites_mois = os.path.join(DIRECTORY, nf_max)
    maxima_par_jour = [max([humi for i, humi in enumerate(humidites) if temps[i].day == jour]) for jour in jours]
    plt.axis([0, nombre_jour_par_mois[mois-1], 0, 100])
    plt.grid(True)
    plt.title(u"Humidite maximale en "+conversion_mois[mois-1]+" "+str(annee)+".")
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(jours, maxima_par_jour, marker="*")
    plt.savefig(nom_maxima_humidites_mois)
    plt.close()

    nf_moy = "moyennes_humidite_mois_"+str(annee)+"_"+str(mois)+".png"
    nom_moyennes_humidites_mois = os.path.join(DIRECTORY, nf_moy)
    moyennes_par_jour = [np.mean([humi for i, humi in enumerate(humidites) if temps[i].day == jour]) for jour in jours]
    plt.axis([0, nombre_jour_par_mois[mois-1], 0, 100])
    plt.grid(True)
    plt.title(u"Humidite moyenne en "+conversion_mois[mois-1]+" "+str(annee)+".")
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.plot(jours, moyennes_par_jour, marker="*")
    plt.savefig(nom_moyennes_humidites_mois)
    plt.close()

    return nf_min, nf_max, nf_moy
#[]

def obtenir_courbe_humidite_annee(temps, humidites, annee):
    # jour en datetime.datetime.now()

    mois_presents = list(set([timme.month for timme in temps]))
    mois_presents.sort()

    #temps_repartis_par_mois = [[j for j, te in enumerate(temps) if te.month == i].sort(lambda x: x.day) for i in mois_presents]
    nf_min = "nom_humidite_annee_minima_"+str(annee)+".png"
    nom_minima = os.path.join(DIRECTORY, nf_min)
    minima_mensuels = [min([humi for j, humi in enumerate(humidites) if temps[j].month == i]) for i in mois_presents]
    plt.axis([0,12, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.title(u"Courbe d'humidite de l'annee "+str(annee)+".")
    plt.plot(mois_presents, minima_mensuels, marker="*")
    plt.savefig(nom_minima)
    plt.close()

    nf_max = "nom_humidite_annee_maxima_"+str(annee)+".png"
    nom_maxima = os.path.join(DIRECTORY, nf_max)
    maxima_mensuels = [max([humi for j, humi in enumerate(humidites) if temps[j].month == i]) for i in mois_presents]
    plt.axis([0,12, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.title(u"Courbe d'humidite de l'annee "+str(annee)+".")
    plt.plot(mois_presents, maxima_mensuels, marker="*")
    plt.savefig(nom_maxima)
    plt.close()

    nf_moy = "nom_humidite_annee_moyennes_"+str(annee)+".png"
    nom_moyennes = os.path.join(DIRECTORY, nf_moy)
    moyennes_mensuels = [np.mean([humi for j, humi in enumerate(humidites) if temps[j].month == i]) for i in mois_presents]
    plt.axis([0,12, 0, 100])
    plt.grid(True)
    plt.xlabel(u"temps")
    plt.ylabel(u"humidite en %")
    plt.title(u"Courbe d'humidite de l'annee "+str(annee)+".")
    plt.plot(mois_presents, moyennes_mensuels, marker="*")
    plt.savefig(nom_moyennes)
    plt.close()

    return nf_min, nf_max, nf_moy



