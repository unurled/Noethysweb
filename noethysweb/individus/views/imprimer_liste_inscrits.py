# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import json
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from core.models import Parametre
from core.views.base import CustomView
from individus.forms.imprimer_liste_inscrits import Formulaire
import csv
import os
from django.conf import settings
from individus.utils import utils_impression_inscrits


def get_data_profil(donnees=None, request=None):
    """ Récupère les données à sauvegarder dans le profil de configuration """
    form = Formulaire(donnees, request=request)
    if not form.is_valid():
        return JsonResponse({"erreur": "Les paramètres ne sont pas valides"}, status=401)

    data = form.cleaned_data
    data["activite"] = data["activite"].pk
    data.pop("profil")
    data.pop("date_situation")
    return data


def Generer_csv(request):
    if request.method == 'POST':
        form = Formulaire(request.POST, request=request)
        if form.is_valid():
            if not form.cleaned_data.get("colonnes_perso"):
                return JsonResponse({"erreur": "Vous devez créer au moins une colonne."}, status=400)

            try:
                impression = utils_impression_inscrits.Impression(dict_donnees=form.cleaned_data)
                impression.Draw()  # Assurez-vous d'appeler cette méthode pour remplir data_tableau

                # Générer le fichier CSV et obtenir son chemin
                csv_file_path = os.path.join(settings.MEDIA_ROOT, 'inscriptions.csv')
                with open(csv_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    headers = [col["nom"] for col in form.cleaned_data["colonnes_perso"]]
                    writer.writerow(headers)
                    for row in impression.data_tableau[1:]:  # saute la ligne d’en-tête
                        writer.writerow([
                            cell.text if hasattr(cell, "text") else cell
                            for cell in row  # Assurez-vous de parcourir chaque cellule de la ligne
                        ])

                # Construire l'URL du fichier CSV
                csv_url = request.build_absolute_uri(settings.MEDIA_URL + 'inscriptions.csv')
                return JsonResponse({"url_csv": csv_url})
            except Exception as e:
                return JsonResponse({"erreur": str(e)}, status=500)
        else:
            return JsonResponse({"erreur": "Veuillez compléter les paramètres."}, status=400)
    else:
        return JsonResponse({"erreur": "Méthode non autorisée."}, status=405)

def Generer_pdf(request):
    # Récupération des paramètres
    form = Formulaire(request.POST, request=request)
    if not form.is_valid():
        return JsonResponse({"erreur": "Veuillez compléter les paramètres."}, status=401)
    if not form.cleaned_data["colonnes_perso"]:
        return JsonResponse({"erreur": "Vous devez créer au moins une colonne."}, status=401)

    # Création du PDF
    from individus.utils import utils_impression_inscrits
    impression = utils_impression_inscrits.Impression(titre="Liste des inscrits", dict_donnees=form.cleaned_data)
    if impression.erreurs:
        return JsonResponse({"erreur": impression.erreurs[0]}, status=401)
    nom_fichier = impression.Get_nom_fichier()
    return JsonResponse({"nom_fichier": nom_fichier})


class View(CustomView, TemplateView):
    menu_code = "imprimer_liste_inscrits"
    template_name = "individus/imprimer_liste_inscrits.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context["page_titre"] = "Imprimer une liste d'inscrits"
        context["box_titre"] = "Imprimer une liste d'inscrits"
        context["box_introduction"] = "Sélectionnez une activité et créez les colonnes du document. Il est possible de mémoriser ces paramètres grâce au profil de configuration."

        # Copie le request_post pour préparer l'application du profil de configuration
        request_post = self.request.POST.copy()
        initial_data = None

        # Sélection du profil de configuration
        if request_post.get("profil"):
            profil = Parametre.objects.filter(idparametre=int(request_post.get("profil"))).first()
            initial_data = json.loads(profil.parametre or "{}")
            initial_data["profil"] = profil.pk
            initial_data["colonnes_perso"] = json.dumps(initial_data["colonnes_perso"])

        # Intégration des formulaires
        context["form"] = Formulaire(data=initial_data, request=self.request)
        return context

    def post(self, request, **kwargs):
        form = Formulaire(request.POST, request=self.request)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())

        context = {"form": form}
        return self.render_to_response(self.get_context_data(**context))
