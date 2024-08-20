# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from core.views.base import CustomView
from django.views.generic import TemplateView
from facturation.forms.liste_tarifs import Formulaire
from core.models import Prestation, Famille, Individu, Tarif, Facture, TarifLigne
from core.utils import utils_dates, utils_texte
from collections import defaultdict


class View(CustomView, TemplateView):
    menu_code = "liste_prestations"
    template_name = "facturation/liste_prestations.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context['page_titre'] = "Liste des prestations"
        if "form_parametres" not in kwargs:
            context['form_parametres'] = Formulaire(request=self.request)
        return context

    def post(self, request, **kwargs):
        form = Formulaire(request.POST, request=self.request)
        if form.is_valid() == False:
            return self.render_to_response(self.get_context_data(form_parametres=form))

        resultats = self.Get_resultats(parametres=form.cleaned_data)
        context = {
            "form_parametres": form,
            "resultats": resultats,
        }
        return self.render_to_response(self.get_context_data(**context))

    def Get_resultats(self, parametres={}):
        activite = parametres["activite"]
        familles = parametres.get("familles", [])
        solde_zero = parametres.get("solde_zero", False)

        prestations = Prestation.objects.filter(activite=activite).select_related('individu', 'tarif', 'facture')

        if familles:
            prestations = prestations.filter(individu__famille__in=familles)

        if solde_zero:
            prestations = prestations.exclude(facture__solde_actuel=0)

        source = []
        source.append(u"<FONT SIZE=+1><B><center>Prestations de l'activité %s</center></B></FONT><BR>" % activite.nom)

        if len(prestations) == 0:
            source.append(u"<P>Aucune prestation</P>")

        tableau = [["Famille", "Individu", "Détails des Prestations", "Somme des prestations", "Soldes des factures"]]

        # Dictionnaire pour agréger les prestations par famille et individu
        prestations_agreggees = defaultdict(lambda: {
            "details": [],
            "montant_total": 0,
            "solde_total": 0
        })

        for prestation in prestations:
            individu = prestation.individu
            famille = prestation.famille
            tarif = prestation.label
            montant = prestation.montant
            facture = prestation.facture
            solde_facture = facture.solde_actuel if facture else 0

            key = (famille.nom, individu.prenom)

            detail = (
                f"<b>Tarif:</b> {tarif}<br>"
                f"<b>Montant:</b> {utils_texte.Formate_montant(montant)}"
                f"<b> - Reste à payer :</b> {utils_texte.Formate_montant(solde_facture)}<br>"
                f"<br>"
            )

            prestations_agreggees[key]["details"].append(detail)
            prestations_agreggees[key]["montant_total"] += montant
            prestations_agreggees[key]["solde_total"] += solde_facture

        for (famille_nom, individu_prenom), valeurs in prestations_agreggees.items():
            details = "".join(valeurs["details"])
            ligne = [
                famille_nom,  # Nom de la famille
                individu_prenom,  # Prénom de l'individu
                details,  # Détails des prestations avec retour à la ligne
                utils_texte.Formate_montant(valeurs["montant_total"]),  # Total des montants formaté
                utils_texte.Formate_montant(valeurs["solde_total"])  # Total des soldes formaté
            ]
            tableau.append(ligne)

        source.append(u"<p><table class='table table-bordered'>")
        source.append("<thead><tr>")
        for titre in tableau[0]:
            source.append(f"<th>{titre}</th>")
        source.append("</tr></thead>")

        source.append("<tbody>")
        for ligne in tableau[1:]:
            source.append("<tr>")
            for index, valeur in enumerate(ligne):
                if index == 2:  # Colonne des détails
                    source.append(f"<td style='text-align:left;'>{valeur}</td>")
                else:
                    source.append(f"<td>{valeur}</td>")
            source.append("</tr>")
        source.append("</tbody></table></p>")

        return "".join(source)