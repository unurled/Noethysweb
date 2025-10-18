# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django import forms
from django.forms import ModelForm
from core.forms.base import FormulaireBase
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden, Submit, HTML, Fieldset, Div, ButtonHolder
from crispy_forms.bootstrap import Field, InlineRadios
from core.utils.utils_commandes import Commandes
from core.models import Individu, QuestionnaireQuestion, QuestionnaireReponse, Inscription, Individu, Activite
from parametrage.forms import questionnaires


class Formulaire(FormulaireBase, forms.Form):
    def __init__(self, *args, **kwargs):
        self.idfamille = kwargs.pop("idfamille")
        self.idindividu = kwargs.pop("idindividu")

        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'individu_questionnaire_form'
        self.helper.form_method = 'post'
        # Création des champs
        # Récupération de l'individu depuis le rattachement
        idindividu = Individu.objects.get(pk=self.idindividu)
        statut_individu = idindividu.statut
        inscriptions = Inscription.objects.filter(individu=idindividu)
        activite_ids = inscriptions.values_list('activite', flat=True).distinct()
        activites = Activite.objects.filter(idactivite__in=activite_ids, structure__visible=True)

        if statut_individu != 5:
            # Si toutes les activités ont 'interne=False', exclure les questions avec 'activite=None'
            condition_activite = Q(activite__in=activites)
            condition_activite &= Q(activite__isnull=False)
        else:
            # Si l'individu a le statut 5, vérifier si toutes les activités ont 'interne=False'
            if activites.filter(interne=False).count() == len(activites):
                condition_activite = Q(activite__in=activites)
                condition_activite &= Q(activite__isnull=False)
            else:
                # Si certaines activités ont 'interne=True', autoriser les questions sans activité
                condition_activite = Q(activite__in=activites)
                condition_activite &= Q(activite__isnull=True)

        condition_structure = (
                Q(structure__in=self.request.user.structures.all()) &
                condition_activite
        )

        for question in QuestionnaireQuestion.objects.filter(condition_structure, categorie="individu", visible=True).order_by("ordre"):
            nom_controle, ctrl = questionnaires.Get_controle(question)
            if ctrl:
                self.fields[nom_controle] = ctrl
        # Importation des réponses
        for reponse in QuestionnaireReponse.objects.filter(individu_id=self.idindividu):
            key = "question_%d" % reponse.question_id
            if key in self.fields:
                self.fields[key].initial = reponse.Get_reponse_for_ctrl()

        # Affichage
        self.helper.layout = Layout()

        if not self.fields:
            self.helper.layout.append(HTML("<strong>Aucun questionnaire n'a été paramétré.</strong>"))
        else:
            # Création des boutons de commande
            if self.mode == "CONSULTATION":
                commandes = Commandes(modifier_url="individu_questionnaire_modifier", modifier_args="idfamille=idfamille idindividu=idindividu", modifier=True,                                  enregistrer=False, annuler=False, ajouter=False)
                self.Set_mode_consultation()
            else:
                commandes = Commandes(annuler_url="{% url 'individu_questionnaire' idfamille=idfamille idindividu=idindividu %}", ajouter=False)
            self.helper.layout.append(commandes)
            # Création des contrôles
            for (nom_controle, ctrl) in self.fields.items():
                self.helper.layout.append(Field(nom_controle))

    def clean(self):
        for key, valeur in self.cleaned_data.items():
            if key.startswith("question_"):
                if isinstance(valeur, list):
                    self.cleaned_data[key] = ";".join(valeur)
        return self.cleaned_data

