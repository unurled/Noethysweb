# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import json
from decimal import Decimal
from django.views.generic import TemplateView
from django.db.models import Q, Sum
from core.views.base import CustomView
from core.models import Famille, Prestation, Reglement, Ventilation, ModeleEmail, Mail, Destinataire
from facturation.forms.liste_soldes import Formulaire
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages

class View(CustomView, TemplateView):
    menu_code = "liste_soldes"
    template_name = "facturation/liste_soldes.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context['page_titre'] = "Liste des soldes"
        if "form_parametres" not in kwargs:
            context['form_parametres'] = Formulaire(request=self.request)
        return context

    def post(self, request, **kwargs):
        form = Formulaire(request.POST, request=self.request)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form_parametres=form))

        data = self.Get_resultats(parametres=form.cleaned_data)
        context = {
            "form_parametres": form,
            "data": data,
            "titre": "Liste des soldes",
        }
        return self.render_to_response(self.get_context_data(**context))

    def Get_resultats(self, parametres={}):
        # Calcul des soldes
        familles = Famille.objects.all()
        conditions_prestations = Q(date__lte=parametres["date_situation"])
        activites= parametres.get("activites", [])
        activites_data = json.loads(activites)
        ids_activites = activites_data.get("ids", [])
        if ids_activites:
            presta = Prestation.objects.filter(activite__in=ids_activites)

        if ids_activites:
            conditions_prestations &= Q(activite__in=ids_activites)

        if parametres["uniquement_factures"]:
            conditions_prestations &= Q(facture__isnull=False)

        dict_prestations = {temp["famille"]: temp["total"] for temp in Prestation.objects.filter(conditions_prestations).values('famille').annotate(total=Sum("montant"))}

        if ids_activites:
            dict_reglements = {
                temp["famille"]: temp["total"]
                for temp in Ventilation.objects.filter(
                    prestation__in=presta
                )
                .values('famille')
                .annotate(total=Sum("montant"))
            }
        else:
            # Si pas d'activités spécifiées, récupérer les ventilations sans ce filtre
            dict_reglements = {
                temp["famille"]: temp["total"]
                for temp in Ventilation.objects.filter(prestation__in=Prestation.objects.filter(conditions_prestations))
                .values('famille')
                .annotate(total=Sum("montant"))
            }
        # Création des colonnes
        liste_colonnes = ["Famille", "Solde", "Prestations", "Règlements"]

        # Création des lignes
        liste_lignes = []
        for famille in familles:
            total_prestations = dict_prestations.get(famille.pk, Decimal(0))
            total_reglements = dict_reglements.get(famille.pk, Decimal(0))
            solde = total_reglements - total_prestations
            if (solde < Decimal(0) and parametres["afficher_debits"]) or (solde > Decimal(0) and parametres["afficher_credits"]) or (solde == Decimal(0) and parametres["afficher_nuls"]):
                liste_lignes.append({
                    "0": famille.nom,
                    "1": float(solde),
                    "2": float(total_prestations),
                    "3": float(total_reglements),
                })

        # Préparation des résultats
        data = {
            "liste_colonnes": liste_colonnes,
            "liste_lignes": json.dumps(liste_lignes),
        }
        return data

def Envoi_emails(request):
    familles = Famille.objects.all()  # Adapter selon vos critères de sélection
    dict_prestations = {
        temp["famille"]: temp["total"]
        for temp in Prestation.objects.values("famille").annotate(total=Sum("montant"))
    }
    dict_reglements = {
        temp["famille"]: temp["total"]
        for temp in Ventilation.objects.values("famille").annotate(total=Sum("montant"))
    }

    liste_anomalies = []

    #Intégration des données
    familles = Famille.objects.all()  # Adapter selon vos critères de sélection
    dict_prestations = {
        temp["famille"]: temp["total"]
        for temp in Prestation.objects.values("famille").annotate(total=Sum("montant"))
    }
    dict_reglements = {
        temp["famille"]: temp["total"]
        for temp in Ventilation.objects.values("famille").annotate(total=Sum("montant"))
    }

    # Création du mail
    logger.debug("Création d'un nouveau mail...")
    modele_email = ModeleEmail.objects.filter(categorie="rappel", defaut=True).first()
    mail = Mail.objects.create(
        categorie="rappel",
        objet=modele_email.objet if modele_email else "",
        html=modele_email.html if modele_email else "",
        adresse_exp=request.user.Get_adresse_exp_defaut(),
        selection="NON_ENVOYE",
        verrouillage_destinataires=True,
        utilisateur=request.user,
    )

    for famille in familles:
        total_prestations = dict_prestations.get(famille.pk, Decimal(0))
        total_reglements = dict_reglements.get(famille.pk, Decimal(0))
        solde = total_reglements - total_prestations

        # Préparer les valeurs de fusion
        valeurs_fusion = {
            "{NOM_FAMILLE}": famille.nom,
            "{SOLDE_CHIFFRES}": f"{solde:.2f}".replace(".", ","),
        }
        if famille.mail:
            destinataire = Destinataire.objects.create(categorie="famille", famille=famille, adresse=famille.mail, valeurs=json.dumps(valeurs_fusion))
            mail.destinataires.add(destinataire)
        else:
            liste_anomalies.append(famille.nom)

    if liste_anomalies:
        messages.add_message(request, messages.ERROR, "Adresses mail manquantes : %s" % ", ".join(liste_anomalies))

    # Création de l'URL pour ouvrir l'éditeur d'emails
    logger.debug("Redirection vers l'éditeur d'emails...")
    url = reverse_lazy("editeur_emails", kwargs={'pk': mail.pk})
    return JsonResponse({"url": url})