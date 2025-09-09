# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import copy
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Hidden
from crispy_forms.bootstrap import Field
from core.widgets import ColorPickerWidget
from core.utils import utils_parametres
from core.forms.base import FormulaireBase


class Formulaire(FormulaireBase, forms.Form):
    memoriser_parametres = forms.BooleanField(label="Mémoriser les paramètres", initial=True, required=False)

    affichage_solde = forms.ChoiceField(label="Afficher le solde", choices=[("0", "Actuel"), ("1", "Initial")], initial="actuel", required=False)
    afficher_impayes = forms.BooleanField(label="Afficher le rappel des impayés", initial=True, required=False)
    integrer_impayes = forms.BooleanField(label="Intégrer les impayés au solde", initial=True, required=False)
    afficher_deja_paye = forms.BooleanField(label="Afficher la case du montant déjà réglé", initial=False, required=False)
    afficher_reste_regler = forms.BooleanField(label="Afficher la case du solde à régler", initial=False, required=False)
    afficher_coupon_reponse = forms.BooleanField(label="Afficher le coupon-réponse", initial=False, required=False)
    afficher_messages = forms.BooleanField(label="Afficher les messages", initial=True, required=False)
    afficher_codes_barres = forms.BooleanField(label="Afficher les codes-barres", initial=False, required=False)
    afficher_reglements = forms.BooleanField(label="Afficher les règlements", initial=True, required=False)
    afficher_avis_prelevements = forms.BooleanField(label="Afficher les avis de prélèvements", initial=False, required=False)
    afficher_qf_dates = forms.BooleanField(label="Afficher les quotients familiaux", initial=True, required=False)

    afficher_titre = forms.BooleanField(label="Afficher le titre", initial=True, required=False)
    texte_titre = forms.CharField(label="Titre du document", initial="Attestation de présence", required=True)
    taille_texte_titre = forms.IntegerField(label="Taille de texte du titre", initial=19, required=True)
    afficher_periode = forms.BooleanField(label="Afficher la période de facturation", initial=True, required=False)
    taille_texte_periode = forms.IntegerField(label="Taille de texte de la période", initial=8, required=True)

    affichage_prestations = forms.ChoiceField(label="Affichage des prestations", choices=[("0", "Détaillé"), ("1", "Regroupement par label"), ("2", "Regroupement par label et par montant unitaire")], initial="0", required=True)
    intitules = forms.ChoiceField(label="Intitulé des prestations", choices=[("0", "Intitulé original"), ("1", "Intitulé original + état absence injustifiée"), ("2", "Nom du tarif"), ("3", "Nom de l'activité")], initial="0", required=True)
    couleur_fond_1 = forms.CharField(label="Couleur de fond 1", required=True, widget=ColorPickerWidget(), initial="#D9D9D9")
    couleur_fond_2 = forms.CharField(label="Couleur de fond 2", required=True, widget=ColorPickerWidget(), initial="#F1F1F1")
    largeur_colonne_date = forms.IntegerField(label="Largeur de la colonne Date", initial=50, required=True)
    largeur_colonne_montant_ht = forms.IntegerField(label="Largeur de la colonne Montant HT", initial=50, required=True)
    largeur_colonne_montant_tva = forms.IntegerField(label="Largeur de la colonne Montant TVA", initial=50, required=True)
    largeur_colonne_montant_ttc = forms.IntegerField(label="Largeur de la colonne Montant TTC", initial=70, required=True)
    taille_texte_individu = forms.IntegerField(label="Taille de texte de l'individu", initial=9, required=True)
    taille_texte_activite = forms.IntegerField(label="Taille de texte de l'activité", initial=6, required=True)
    taille_texte_noms_colonnes = forms.IntegerField(label="Taille de texte des noms de colonnes", initial=5, required=True)
    taille_texte_prestation = forms.IntegerField(label="Taille de texte des prestations", initial=7, required=True)
    taille_texte_messages = forms.IntegerField(label="Taille de texte des messages", initial=7, required=True)
    taille_texte_labels_totaux = forms.IntegerField(label="Taille de texte des labels totaux", initial=9, required=True)
    taille_texte_montants_totaux = forms.IntegerField(label="Taille de texte des montants totaux", initial=10, required=True)

    taille_texte_prestations_anterieures = forms.IntegerField(label="Taille de texte du commentaire", initial=5, required=True)
    texte_prestations_anterieures = forms.CharField(label="Texte d'information", initial="Des prestations antérieures ont été reportées sur cette attestation.", required=True)

    texte_introduction = forms.CharField(label="Texte d'introduction", initial="Je soussigné(e) {SIGNATAIRE}, atteste avoir accueilli {NOMS_INDIVIDUS} selon le détail suivant :", required=False)
    taille_texte_introduction = forms.IntegerField(label="Taille de texte d'introduction", initial=9, required=True)
    style_texte_introduction = forms.ChoiceField(label="Style du texte d'introduction", choices=[("0", "Normal"), ("1", "Italique"), ("2", "Gras"), ("3", "Italique + gras")], initial="0", required=True)
    couleur_fond_introduction = forms.CharField(label="Couleur de fond introduction", required=True, widget=ColorPickerWidget(), initial="#FFFFFF")
    couleur_bord_introduction = forms.CharField(label="Couleur de bord introduction", required=True, widget=ColorPickerWidget(), initial="#FFFFFF")
    alignement_texte_introduction = forms.ChoiceField(label="Alignement du texte d'introduction", choices=[("0", "Gauche"), ("1", "Centre"), ("2", "Droite")], initial="0", required=True)

    texte_conclusion = forms.CharField(label="Texte complémentaire", initial="", required=False, help_text="Saisissez du texte complémentaire à ajouter (N° de déclaration, directeur, dates,...)")
    taille_texte_conclusion = forms.IntegerField(label="Taille de texte de conclusion", initial=9, required=True)
    style_texte_conclusion = forms.ChoiceField(label="Style du texte de conclusion", choices=[("0", "Normal"), ("1", "Italique"), ("2", "Gras"), ("3", "Italique + gras")], initial="0", required=True)
    couleur_fond_conclusion = forms.CharField(label="Couleur de fond conclusion", required=True, widget=ColorPickerWidget(), initial="#FFFFFF")
    couleur_bord_conclusion = forms.CharField(label="Couleur de bord conclusion", required=True, widget=ColorPickerWidget(), initial="#FFFFFF")
    alignement_texte_conclusion = forms.ChoiceField(label="Alignement du texte de conclusion", choices=[("0", "Gauche"), ("1", "Centre"), ("2", "Droite")], initial="0", required=True)


    def __init__(self, *args, **kwargs):
        self.memorisation = kwargs.pop("memorisation", True)
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'options_impression_form'
        self.helper.form_method = 'post'

        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-md-4'
        # self.helper.field_class = 'col-md-8'

        # Importation des paramètres
        if self.memorisation:
            parametres = {nom: field.initial for nom, field in self.fields.items()}
            del parametres["memoriser_parametres"]
            parametres = utils_parametres.Get_categorie(categorie="impression_attestation", utilisateur=self.request.user, parametres=parametres)
            for nom, valeur in parametres.items():
                self.fields[nom].initial = valeur
        # Champs visibles
        visible_fields = [
            "affichage_solde",
            "afficher_deja_paye",
            "afficher_reste_regler",
            "afficher_reglements",
            "texte_conclusion",
            "memoriser_parametres",
        ]

        # Champs à cacher = tout le reste
        hidden_fields = [f for f in self.fields if f not in visible_fields]

        # Génération des Hidden
        layout_fields = [Hidden(f, value=self.fields[f].initial) for f in hidden_fields]

        # Layout principal
        self.helper.layout = Layout(
            *layout_fields,  # tous les champs cachés
            Fieldset("Eléments à afficher",
                     Field("afficher_deja_paye"),
                     Field("afficher_reste_regler"),
                     Field("afficher_reglements"),
                     ),

            Fieldset("Textes",
                     Field("texte_conclusion"),
                     Field("affichage_solde"),
                     ),
        )
        # Si mémorisation, on l’ajoute en premier
        if self.memorisation:
            self.helper.layout.insert(0,
                                      Fieldset("Mémorisation",
                                               Field("memoriser_parametres"),
                                               ),
                                      )

    def clean(self):
        if self.memorisation and self.cleaned_data["memoriser_parametres"]:
            parametres = copy.copy(self.cleaned_data)
            del parametres["memoriser_parametres"]
            utils_parametres.Set_categorie(categorie="impression_attestation", utilisateur=self.request.user, parametres=parametres)
