# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import datetime, json
from django import forms
from django.forms import ModelForm
from django.db.models import Q
from core.forms.base import FormulaireBase
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Fieldset
from crispy_forms.bootstrap import Field, PrependedText
from core.utils.utils_commandes import Commandes
from core.utils import utils_preferences
from core.models import ComptaOperation, ComptaTiers, ComptaVentilation, ComptaAnalytique, ComptaCategorie
from core.widgets import DatePickerWidget, Select_avec_commandes_advanced
from comptabilite.widgets import Ventilation_operation


class Formulaire(FormulaireBase, ModelForm):
    ventilation = forms.CharField(label="        ", required=False, widget=Ventilation_operation(attrs={}))
    categorie_rapide = forms.ModelChoiceField(
        queryset=ComptaCategorie.objects.none(),
        required=False,
        label="Catégorie"
    )

    class Meta:
        model = ComptaOperation
        fields = "__all__"
        widgets = {
            "date": DatePickerWidget(),
            "observations": forms.Textarea(attrs={'rows': 3}),
            "tiers": Select_avec_commandes_advanced(attrs={"id_form": "tiers_form", "module_form": "parametrage.forms.tiers", "nom_objet": "un tiers", "champ_nom": "nom"}),
            "mode": Select_avec_commandes_advanced(attrs={"id_form": "modes_reglements_form", "module_form": "parametrage.forms.modes_reglements", "nom_objet": "un mode de règlement", "champ_nom": "label"}),
        }

    def __init__(self, *args, **kwargs):
        idcompte = kwargs.pop("categorie")
        type = kwargs.pop("type")
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "operations_tresorerie_form"
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        # Type
        if self.instance.pk:
            type = self.instance.type

        # Date
        self.fields["date"].initial = datetime.date.today()

        # Tiers
        self.fields["tiers"].queryset = ComptaTiers.objects.filter(Q(structure__in=self.request.user.structures.all()) | Q(structure__isnull=True)).order_by("nom")

        # Ventilation
        self.fields["ventilation"].widget.request = self.request
        self.fields["ventilation"].widget.attrs.update({
            "analytiques": json.dumps({analytique.pk: analytique.nom for analytique in ComptaAnalytique.objects.all()}),
            "categories": json.dumps({categorie.pk: categorie.nom for categorie in ComptaCategorie.objects.all()}),
        })
        ventilations = ComptaVentilation.objects.select_related("analytique", "categorie").filter(operation=self.instance if self.instance else 0)
        self.fields["ventilation"].initial = json.dumps([{"idventilation": v.pk, "date_budget": str(v.date_budget), "analytique": v.analytique_id, "categorie": v.categorie_id, "montant": str(v.montant)} for v in ventilations])

        self.fields["categorie_rapide"].queryset = ComptaCategorie.objects.filter(
            Q(type=type) & (Q(structure__in=self.request.user.structures.all()) | Q(structure__isnull=True))
        ).order_by("nom")

        # Affichage
        self.helper.layout = Layout(
            Commandes(annuler_url="{{ view.get_success_url }}"),
            Hidden("compte", value=idcompte),
            Hidden("type", value=type),
            Fieldset("Généralités",
                Field("date"),
                Field("num_piece"),
                Field("libelle"),
                # Field("tiers"),
                Field("mode"),

                PrependedText("montant", utils_preferences.Get_symbole_monnaie()),
            ),
            Fieldset("Ventilation unique",
                     Field("categorie_rapide"),
            ),
            Fieldset("Ventilation multiple",
                Field("ventilation"),
            ),
            # Fieldset("Options",
            #     Field("releve"),
            #     Field("ref_piece"),
            #     Field("observations"),
            # ),
        )

    def clean(self):
        montant = self.cleaned_data.get("montant")
        if not montant:
            self.add_error("montant", "Vous devez saisir un montant.")

        ventilation_data = self.cleaned_data.get("ventilation")
        categorie_rapide = self.cleaned_data.get("categorie_rapide")

        # Vérification : soit ventilation complète, soit catégorie rapide + montant
        if not ventilation_data and not categorie_rapide:
            self.add_error(None, "Vous devez saisir une ventilation complète ou choisir une catégorie rapide.")

        # Si catégorie rapide sélectionnée mais pas de montant, erreur
        if categorie_rapide and not montant:
            self.add_error(None, "Vous devez saisir un montant pour la catégorie rapide.")

        return self.cleaned_data
