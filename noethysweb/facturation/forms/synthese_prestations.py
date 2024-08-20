# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Submit, HTML, Row, Column, Fieldset, Div, ButtonHolder
from crispy_forms.bootstrap import Field
from core.utils.utils_commandes import Commandes
from core.widgets import DateRangePickerWidget, SelectionActivitesWidget
from core.forms.select2 import Select2MultipleWidget
from core.utils import utils_questionnaires
from core.forms.base import FormulaireBase


def Get_regroupements():
    liste_regroupements = [
        ("famille", "Famille"), ("individu", "Individu"),
        ("label_prestation", "Nom de la prestation"), ("activite", "Activité"),
        ("jour", "Jour"), ("mois", "Mois"), ("annee", "Année"),
]

    # Intégration des questionnaires
    q = utils_questionnaires.Questionnaires()
    for public in ("famille", "individu"):
        for dictTemp in q.GetQuestions(public):
            label = "Question %s. : %s" % (public[:3], dictTemp["label"])
            code = "question_%s_%d" % (public, dictTemp["IDquestion"])
            liste_regroupements.append((code, label))

    return liste_regroupements


def Get_modes():
    liste_modes = [
        ("nbre", "Nombre de prestations"), ("facture", "Montant des prestations"),
        ("solde_facture", "Solde de la facture"),
        ("regle", "Montant des prestations réglées"), ("impaye", "Montant des prestations impayées"),
        ("nbre_facturees", "Nombre de prestations facturées"),
        ("facture_facturees", "Montant des prestations facturées"),
        ("regle_facturees", "Montant des prestations réglées et facturées"),
        ("impaye_facturees", "Montant des prestations impayées et facturées"),
        ("nbre_nonfacturees", "Nombre de prestations non facturées"),
        ("facture_nonfacturees", "Montant des prestations non facturées"),
        ("regle_nonfacturees", "Montant des prestations réglées et non facturées"),
        ("impaye_nonfacturees", "Montant des prestations impayées et non facturées"), ]
    return liste_modes


class Formulaire(FormulaireBase, forms.Form):
    activites = forms.CharField(label="Activités", required=True, widget=SelectionActivitesWidget(attrs={"afficher_colonne_detail": False}))
    donnee_ligne = forms.ChoiceField(label="Ligne", choices=Get_regroupements(), initial="famille", required=False)
    donnee_colonne = forms.ChoiceField(label="Colonne", choices=Get_regroupements(), initial="activite", required=False)
    #donnee_detail = forms.ChoiceField(label="Ligne de détail", choices=Get_regroupements(), initial="label_prestation", required=False)
    donnee_case = forms.CharField(widget=forms.HiddenInput(), initial="facture")
    donnee_detail = forms.CharField(widget=forms.HiddenInput(), initial="label_prestation")
    masquer_solde_superieur_zero = forms.BooleanField(required=False,label="Afficher uniquement les familles avec un solde à payer")

    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_parametres'
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Fieldset("Données",
                Field('activites'),
            ),
            Fieldset("Affichage",
                     Field('masquer_solde_superieur_zero'),

                     Field('donnee_ligne'),
                Field('donnee_colonne'),
                Field('donnee_detail'),
                Field('donnee_case'),
            ),
        )


