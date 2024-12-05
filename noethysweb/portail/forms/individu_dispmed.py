# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from core.models import Individu, TypeDispmed
from core.widgets import Select_many_avec_plus
from portail.forms.fiche import FormulaireBase


class Formulaire(FormulaireBase, ModelForm):
    dispmed = forms.ModelMultipleChoiceField(label=_("Dispositifs médicaux"),
                    widget=Select_many_avec_plus(attrs={"url_ajax": "portail_ajax_ajouter_dispmed", "afficher_bouton_ajouter": False, "textes": {"champ": _("Nom du dispositif médical"), "ajouter": _("Ajouter un dispositif médical")}}),
                    queryset=TypeDispmed.objects.all().order_by("nom"), required=False)
    class Meta:
        model = Individu
        fields = ["dispmed", "dispmed_detail"]

    def __init__(self, *args, **kwargs):
        self.rattachement = kwargs.pop("rattachement", None)
        self.mode = kwargs.pop("mode", "CONSULTATION")
        self.nom_page = "individu_dispmed"
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'individu_dispmed_form'
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.use_custom_control = False

        # Help_texts pour le mode édition
        self.help_texts = {
            "dispmed": _("Cliquez sur le champ ci-dessus pour faire apparaître la liste de choix et cliquez sur un ou plusieurs éléments dans la liste") + ". <a href='#' class='ajouter_element'>" + _("Cliquez ici pour ajouter un dispositif médical manquant dans la liste de choix") + ".</a>",
        }

        # Champs affichables
        self.liste_champs_possibles = [
            {"titre": _("Allergies contractées"), "champs": ["dispmed"]},
            {"titre": _("Données complémentaires"), "champs": ["dispmed_detail"]},
        ]

        # Préparation du layout
        self.Set_layout()
