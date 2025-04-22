# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy, reverse
from core.views.base import CustomView
from django.views.generic import TemplateView
from core.utils import utils_dates, utils_infos_individus, utils_dictionnaires
from individus.forms.liste_inscriptions_attente import Formulaire
from core.models import Inscription, Activite, Groupe, PortailRenseignement, Tarif, Prestation
from django.db.models import Q, Count
import json


class View(CustomView, TemplateView):
    menu_code = "liste_inscriptions_attente"
    template_name = "individus/liste_inscriptions_attente.html"
    etat = "attente"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        if self.etat == "attente":
            context['page_titre'] = "Liste des inscriptions en attente"
        else:
            context['page_titre'] = "Liste des inscriptions refusées"
        if "form_parametres" not in kwargs:
            context['form_parametres'] = Formulaire(request=self.request)
            context['resultats'] = json.dumps(self.Get_resultats(parametres={}))
        return context

    def post(self, request, **kwargs):
        form = Formulaire(request.POST, request=self.request)
        if form.is_valid() == False:
            return self.render_to_response(self.get_context_data(form_parametres=form))
        context = {
            "form_parametres": form,
            "resultats": json.dumps(self.Get_resultats(parametres=form.cleaned_data)),
        }
        return self.render_to_response(self.get_context_data(**context))
    def split_value(self, value):
            try:
                parts = json.loads(value).split(';')  # Supposons que les parties sont séparées par des points-virgules
                if len(parts) < 3:
                    parts.extend([''] * (3 - len(parts)))  # Ajoutez des chaînes vides si moins de 3 parties
                return parts[0], parts[1], parts[2]
            except (json.JSONDecodeError, IndexError):
                return '', '', ''  # Retourne des chaînes vides en cas d'erreur

    def Rechercher_tarifs(self, inscription=None, liste_tarifs=None):
        if inscription:
            prestations = Prestation.objects.filter(
                individu=inscription.individu,
                activite=inscription.activite
            ).select_related('tarif')
            labels_tarifs = [p.tarif.description for p in prestations if p.tarif]
            return " | ".join(labels_tarifs)

        elif liste_tarifs:
            try:
                liste_ids = json.loads(liste_tarifs)

                # Sécurité : forcer des entiers
                liste_ids = [int(x) for x in liste_ids if str(x).isdigit()]
                tarifs = Tarif.objects.filter(pk__in=liste_ids)
                return " | ".join([t.description for t in tarifs])
            except Exception as e:
                print("ERREUR TARIF:", e)
                return ""


    def Get_resultats(self, parametres={}):
        if not parametres:
            return []

        # Récupération des paramètres
        param_activites = json.loads(parametres["activites"])
        condition_activites = Q(activite__in=param_activites["ids"])
        liste_activites = Activite.objects.filter(pk__in=param_activites["ids"])

        renseignements = PortailRenseignement.objects.filter(categorie="activites", code="inscrire_activite", etat="ATTENTE", activite__in=liste_activites)
        # Traitement des résultats
        dictInscriptions = {}
        dictGroupes = {}

        # Pré-traitement des renseignements en attente (simulant des inscriptions en attente)
        for renseignement in renseignements:
            part1, part2, part3 = self.split_value(renseignement.nouvelle_valeur)
            try:
                IDactivite = int(part1)
                IDgroupe = int(part2)
                Tarifs = part3
            except ValueError:
                continue

            utils_dictionnaires.DictionnaireImbrique(dictionnaire=dictInscriptions, cles=[IDactivite, IDgroupe],
                                                     valeur=[])
            dictTemp = {
                "IDinscription": renseignement.pk,
                "IDindividu": renseignement.individu.pk,
                "nom_individu": renseignement.individu.Get_nom(),
                "date_inscription": renseignement.date,
                "IDactivite": IDactivite,
                "IDgroupe": IDgroupe,
                "IDfamille": renseignement.famille.pk,
                "nomCategorie": "Pré-inscription",
                "libelle_tarifs": self.Rechercher_tarifs(liste_tarifs=part3),
            }
            dictInscriptions[IDactivite][IDgroupe].append(dictTemp)

            # Mémorisation du nom de groupe s'il n'est pas déjà connu
            if IDgroupe not in dictGroupes:
                groupe = Groupe.objects.filter(pk=IDgroupe).first()
                if groupe:
                    dictGroupes[IDgroupe] = groupe.nom

        inscriptions = Inscription.objects.select_related('individu', 'activite', 'groupe',).filter(condition_activites, statut=self.etat)

        for inscription in inscriptions:
            utils_dictionnaires.DictionnaireImbrique(dictionnaire=dictInscriptions, cles=[inscription.activite_id, inscription.groupe_id], valeur=[])
            dictTemp = {"IDinscription": inscription.pk, "IDindividu": inscription.individu_id, "nom_individu": inscription.individu.Get_nom(),
                        "date_inscription": inscription.date_debut, "IDactivite": inscription.activite_id, "IDgroupe": inscription.groupe_id,
                        "IDfamille": inscription.famille_id, "nomCategorie": inscription.categorie_tarif.nom, "libelle_tarifs": self.Rechercher_tarifs(inscription=inscription),}
            dictInscriptions[inscription.activite_id][inscription.groupe_id].append(dictTemp)

            # Mémorisation des groupes
            if (inscription.groupe_id in dictGroupes) == False:
                dictGroupes[inscription.groupe_id] = inscription.groupe.nom

        # Recherche des places disponibles
        dictInscrits = {}
        inscriptions_existantes = Inscription.objects.values("groupe").filter(condition_activites, statut="ok").annotate(nbre=Count('pk'))
        for dict_temp in inscriptions_existantes:
            dictInscrits[dict_temp["groupe"]] = dict_temp["nbre"]

        # Recherche les activités
        dictActivites = {}
        for activite in liste_activites:
            dictActivites[activite.pk] = {"nom": activite.nom, "abrege": activite.abrege, "date_debut": activite.date_debut, "date_fin": activite.date_fin,
                                          "nbre_inscrits_max": activite.nbre_inscrits_max, "groupes": {}}

        # Recherche des groupes
        groupes = Groupe.objects.filter(condition_activites)
        for groupe in groupes:

            # Recherche le nombre d'inscrits sur chaque groupe
            if groupe.pk in dictInscrits:
                nbre_inscrits = dictInscrits[groupe.pk]
            else:
                nbre_inscrits = 0

            # Recherche du nombre de places disponibles sur le groupe
            if groupe.nbre_inscrits_max not in (None, 0):
                nbre_places_disponibles = groupe.nbre_inscrits_max - nbre_inscrits
            else:
                nbre_places_disponibles = None

            # Mémorise le groupe
            dictActivites[groupe.activite_id]["groupes"][groupe.pk] = {"nom": groupe.nom, "nbre_places_disponibles": nbre_places_disponibles,
                                                                       "nbre_inscrits": nbre_inscrits, "nbre_inscrits_max": groupe.nbre_inscrits_max}

        for IDactivite in list(dictActivites.keys()):
            # Recherche le nombre d'inscrits total de l'activité
            dictActivites[IDactivite]["nbre_inscrits"] = 0
            for IDgroupe in dictActivites[IDactivite]["groupes"]:
                if IDgroupe in dictInscrits:
                    dictActivites[IDactivite]["nbre_inscrits"] += dictInscrits[IDgroupe]

            # Recherche du nombre de places disponibles sur l'activité
            if dictActivites[IDactivite]["nbre_inscrits_max"] not in (None, 0):
                dictActivites[IDactivite]["nbre_places_disponibles"] = dictActivites[IDactivite]["nbre_inscrits_max"] - dictActivites[IDactivite]["nbre_inscrits"]
            else:
                dictActivites[IDactivite]["nbre_places_disponibles"] = None

        liste_resultats = []

        # Branches Activités
        listeActivites = list(dictInscriptions.keys())
        listeActivites.sort()

        for IDactivite in listeActivites:
            id_activite = "activite_%s" % IDactivite
            liste_resultats.append({"id": id_activite, "pid": 0, "type": "activite", "label": dictActivites[IDactivite]["nom"], "date_saisie": "", "categorie_tarif": "", "action": ""})

            # Branches Groupes
            listeGroupes = list(dictInscriptions[IDactivite].keys())
            listeGroupes.sort()
            num = 1

            for IDgroupe in listeGroupes:
                for dictInscription in dictInscriptions[IDactivite][IDgroupe]:
                    texteIndividu = "%d. %s" % (num, dictInscription["nom_individu"])

                    nbre_places_dispo = self.RechercheSiPlaceDispo(dictActivites[IDactivite], IDgroupe)
                    place_dispo = nbre_places_dispo is None or nbre_places_dispo > 0

                    # Mise à jour des places restantes
                    if place_dispo:
                        if dictActivites[IDactivite]["nbre_places_disponibles"] is not None:
                            dictActivites[IDactivite]["nbre_places_disponibles"] -= 1
                        if dictActivites[IDactivite]["groupes"][IDgroupe]["nbre_places_disponibles"] is not None:
                            dictActivites[IDactivite]["groupes"][IDgroupe]["nbre_places_disponibles"] -= 1

                    icone = "fa-check text-green" if place_dispo else "fa-remove text-red"
                    label = f"<i class='fa {icone} margin-r-5'></i> {texteIndividu}"

                    url = reverse("famille_resume", args=[dictInscription["IDfamille"]])
                    action = f"<a type='button' class='btn btn-default btn-sm' href='{url}' title='Accéder à la fiche famille'><i class='fa fa-folder-open-o'></i></a>"

                    id_inscription = f"inscription_{dictInscription['IDinscription']}"
                    liste_resultats.append({
                        "id": id_inscription,
                        "pid": id_activite,
                        "type": "inscription",
                        "label": label,
                        "date_saisie": utils_dates.DateComplete(dictInscription["date_inscription"]),
                        "categorie_tarif": dictInscription["nomCategorie"],
                        "tarifs": dictInscription["libelle_tarifs"],
                        "action": action
                    })

                    num += 1

        return liste_resultats

    def RechercheSiPlaceDispo(self, dictActivite={}, IDgroupe=None):
        nbre_places_disponibles = []

        if dictActivite["nbre_places_disponibles"] != None:
            nbre_places_disponibles.append(dictActivite["nbre_places_disponibles"])

        for IDgroupeTmp, dictGroupe in dictActivite["groupes"].items():
            if IDgroupeTmp == IDgroupe and dictGroupe["nbre_places_disponibles"] != None:
                nbre_places_disponibles.append(dictGroupe["nbre_places_disponibles"])

        if len(nbre_places_disponibles) > 0:
            return min(nbre_places_disponibles)
        else:
            return None
