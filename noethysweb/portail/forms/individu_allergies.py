# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from core.models import Individu, TypeAllergie
from core.widgets import Select_many_avec_plus
from portail.forms.fiche import FormulaireBase


class Formulaire(FormulaireBase, ModelForm):
    allergies = forms.ModelMultipleChoiceField(label=_("Allergies"),
                    widget=Select_many_avec_plus(attrs={"url_ajax": "portail_ajax_ajouter_allergie", "afficher_bouton_ajouter": False, "textes": {"champ": _("Nom de l'allergie"), "ajouter": _("Ajouter une allergie")}}),
                    queryset=TypeAllergie.objects.all().order_by("nom"), required=False)
    class Meta:
        model = Individu
        fields = ["allergies", "allergies_detail"]

    def __init__(self, *args, **kwargs):
        self.rattachement = kwargs.pop("rattachement", None)
        self.mode = kwargs.pop("mode", "CONSULTATION")
        self.nom_page = "individu_allergies"
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'individu_allergies_form'
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.use_custom_control = False

        # Help_texts pour le mode édition
        self.help_texts = {
            "allergies": _("Cliquez sur le champ ci-dessus pour faire apparaître la liste de choix et cliquez sur un ou plusieurs éléments dans la liste") + ". <a href='#' class='ajouter_element'>" + _("Cliquez ici pour ajouter une allergie manquante dans la liste de choix") + ".</a>",
        }

        # Champs affichables
        self.liste_champs_possibles = [
            {"titre": _("Allergies contractées"), "champs": ["allergies"]},
            {"titre": _("Données complémentaires"), "champs": ["allergies_detail"]},
        ]

        # Préparation du layout
        self.Set_layout()
