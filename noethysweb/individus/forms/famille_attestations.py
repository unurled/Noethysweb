# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Fieldset
from crispy_forms.bootstrap import Field
from core.utils.utils_commandes import Commandes
from core.widgets import SelectionActivitesWidget, DateRangePickerWidget, FormIntegreWidget
from core.forms.base import FormulaireBase
from core.models import Attestation, ModeleDocument, Inscription, Activite
from core.forms.select2 import Select2Widget
from facturation.forms.attestations_options_impression import Formulaire as Form_options_impression

class Formulaire(FormulaireBase, forms.Form):
    activite = forms.ModelChoiceField(queryset=Activite.objects.exclude(nom__icontains="ARCHIVE"),empty_label="Sélectionnez une activité",required=True)
    modele = forms.ModelChoiceField(label="Modèle de document", widget=Select2Widget(), queryset=ModeleDocument.objects.filter(categorie="attestation").order_by("nom"), required=True)
    options_impression = forms.CharField(label="Options d'impression", required=False, widget=FormIntegreWidget())

    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'form_parametres'
        self.helper.form_method = 'post'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        # Charge le modèle de document par défaut
        modele_defaut = ModeleDocument.objects.filter(categorie="attestation", defaut=True)
        if modele_defaut:
            self.fields["modele"].initial = modele_defaut.first()
        self.fields['activite'].queryset = Activite.objects.exclude(nom__icontains="ARCHIVE").filter(structure__in=self.request.user.structures.all()).order_by('nom')
        self.fields['options_impression'].widget.attrs.update({"form": Form_options_impression(request=self.request)})

        self.helper.layout = Layout(
            Commandes(annuler_url="{% url 'individus_toc' %}", enregistrer=False, ajouter=False,
                      commandes_principales=[HTML(
                          """<a type='button' class="btn btn-primary margin-r-5" onclick="generer_pdf()" title="Enregistrer les attestations"></i>Enregistrer les attestations</a>"""),
                      ]),
            Fieldset("Sélection des individus",
                Field('activite'),
            ),
            Fieldset("Options",
                     Field("modele"),
                     Field("options_impression"),
            ),
        )
    def clean(self):
        if self.data.get("infos"):
            self.cleaned_data["infos"] = json.loads(self.data.get("infos"))

        # Vérification du formulaire des options d'impression
        form_options = Form_options_impression(self.data, request=self.request)
        if not form_options.is_valid():
            liste_erreurs = form_options.errors.as_data().keys()
            self.add_error("options_impression", "Veuillez renseigner les champs manquants : %s." % ", ".join(liste_erreurs))

        # Rajoute les options d'impression formatées aux résultats du formulaire
        self.cleaned_data["options_impression"] = form_options.cleaned_data
        return self.cleaned_data