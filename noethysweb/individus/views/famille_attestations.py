# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import json
import logging
import os
import shutil
from pathlib import Path
from django.http import JsonResponse
from django.views.generic import TemplateView
from core.views.base import CustomView
from core.utils import utils_dates
from facturation.utils import utils_facturation, utils_impression_facture
from django.contrib.auth.decorators import login_required
logger = logging.getLogger(__name__)
from django.utils import timezone
from core.data import data_modeles_emails
from individus.forms.famille_attestations import Formulaire
from core.models import Attestation, Inscription, Activite, Individu, Attestationdoc
from core.utils import utils_texte
from django.conf import settings



def obtenir_noms_individus(individus_ids):
    individus = Individu.objects.filter(pk__in=individus_ids)
    noms = [f"{individu.prenom} {individu.nom}" for individu in individus]
    return ", ".join(noms)


def Generer_pdf(request):
    form = Formulaire(request.POST, request=request)
    if not form.is_valid():
        logger.warning("Formulaire invalide: %s", form.errors)
        return JsonResponse({"erreur": "Veuillez compléter les paramètres"}, status=401)

    parametres = form.cleaned_data

    # Validation des données
    parametres["date_edition"] = timezone.now().date()
    parametres["signataire"] = request.user

    # Obtenez le dernier numéro d'attestation
    derniere_attestation = Attestationdoc.objects.last()
    numero_actuel = derniere_attestation.pk + 1 if derniere_attestation else 1

    if not parametres["modele"]:
        return JsonResponse({"erreur": "Vous devez sélectionner un modèle de document"}, status=401)

    # Récupération de la période
    activite = parametres["activite"]
    date_debut = activite.date_debut
    date_fin = activite.date_fin

    inscriptions = Inscription.objects.filter(activite=activite).select_related('famille', 'individu')
    if not inscriptions:
        return JsonResponse({"erreur": "Aucune famille inscrite trouvée pour l'activité spécifiée"}, status=401)

    resultats = []

    for inscription in inscriptions:
        IDfamille = inscription.famille.idfamille
        individus_ids = [inscription.individu.pk]
        activites = [int(activite.pk)]  # Utiliser l'activité sélectionnée

        dict_attestations = utils_facturation.Facturation().GetDonnees(
            liste_activites=activites,
            date_debut=date_debut,
            date_fin=date_fin,
            mode="attestation",
            IDfamille=IDfamille,
            liste_IDindividus=individus_ids,
            filtre_prestations="",
            exclusions_prestations="",
        )

        if not dict_attestations:
            continue  # Passer à la prochaine famille si aucune attestation trouvée

        # Incrémenter le numéro d'attestation pour chaque famille
        parametres["numero"] = numero_actuel
        numero_actuel += 1

        # Extraire les noms des individus
        noms_individus = obtenir_noms_individus(individus_ids)

        # Rajouter les données du formulaire
        dict_attestations[IDfamille].update({
            "{DATE_EDITION}": parametres["date_edition"].strftime('%d/%m/%Y'),
            "{SIGNATAIRE}": str(parametres["signataire"]),
            "{NUM_ATTESTATION}": parametres["numero"],
            "{NOMS_INDIVIDUS}": noms_individus,
            "{DATE_DEBUT}": date_debut.strftime('%d/%m/%Y'),
            "{DATE_FIN}": date_fin.strftime('%d/%m/%Y'),
        })

        # Texte d'introduction fourni
        texte_introduction = "Je soussigné(e) {SIGNATAIRE}, atteste avoir accueilli {NOMS_INDIVIDUS} sur la période du {DATE_DEBUT} au {DATE_FIN} selon le détail suivant :"

        # Assurez-vous que dict_options contient des données valides pour la fusion
        dict_options = parametres["options_impression"]
        if not isinstance(texte_introduction, str):
            return JsonResponse({"erreur": "Le texte d'introduction est invalide."}, status=401)

        # Fusion du texte d'introduction avec les mots-clés
        dict_attestations[IDfamille]["texte_introduction"] = utils_texte.Fusionner_motscles(
            texte_introduction, dict_attestations[IDfamille]
        )

        # Renvoie les infos au template pour la sauvegarde
        infos = {
            "total": float(
                dict_attestations[IDfamille].get("{TOTAL_PERIODE}", "0").replace(' €', '').replace(',', '.')),
            "regle": float(dict_attestations[IDfamille].get("{TOTAL_REGLE}", "0").replace(' €', '').replace(',', '.')),
            "solde": float(dict_attestations[IDfamille].get("{SOLDE_DU}", "0").replace(' €', '').replace(',', '.')),
            "individus": ";".join(
                [str(idindividu) for idindividu in dict_attestations[IDfamille].get("individus", {}).keys()]),
            "activites": ";".join(
                [str(idactivite) for idactivite in dict_attestations[IDfamille].get("liste_idactivite", [])])
        }
        # Création du PDF
        impression = utils_impression_facture.Impression(
            dict_donnees=dict_attestations,
            dict_options=dict_options,
            IDmodele=parametres["modele"].pk,
            mode="attestation"
        )
        nom_fichier = impression.Get_nom_fichier()
        print(nom_fichier)

        # Récupération des valeurs de fusion
        champs = {motcle: dict_attestations[IDfamille].get(motcle, "") for motcle, label in
                  data_modeles_emails.Get_mots_cles("attestation_presence")}

        resultats.append({
            "infos": infos,
            "nom_fichier": nom_fichier,
            "categorie": "attestation_presence",
            "label_fichier": "Attestation de présence",
            "champs": champs,
            "idfamille": IDfamille
        })
        chemin_source = Path(settings.MEDIA_ROOT) / nom_fichier.lstrip('/')

        # Répertoire de destination
        dossier_attestations = Path(settings.MEDIA_ROOT) / 'attestations_presence'

        # Assurez-vous que le répertoire de destination existe
        dossier_attestations.mkdir(parents=True, exist_ok=True)

        # Nom du fichier dans le répertoire de destination
        nom_fichier = f"AttestationI{parametres['numero']}I{parametres['date_edition']}.pdf"
        chemin_destination = dossier_attestations / nom_fichier

        # Copier le fichier
        shutil.copy(chemin_source, chemin_destination)

        print(f"Fichier copié de {chemin_source} à {chemin_destination}")
        # Enregistrer l'attestation dans Attestationdoc
        Attestationdoc.objects.update_or_create(
            famille=inscription.famille,
            activites=activite,
            individus=inscription.individu,
            defaults={'fichier': "attestations_presence/" + nom_fichier}
        )

    if not resultats:
        return JsonResponse({"erreur": "Aucune attestation trouvée pour les familles inscrites"}, status=401)
    return JsonResponse({"resultats": resultats})

class View(CustomView, TemplateView):
    menu_code = "famille_attestations"
    template_name = "individus/famille_attestations.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context['page_titre'] = "Edition des attestations de présence"
        context['box_titre'] = "Edition des attestations de présence"
        context['box_introduction'] = "Renseignez les paramètres et cliquez sur le bouton Générer. La génération des document peut nécessiter quelques instants d'attente."
        if "form" not in kwargs:
            context['form'] = Formulaire(request=self.request)
        return context