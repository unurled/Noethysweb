# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.db.models import Q
from core.models import QuestionnaireReponse, QuestionnaireQuestion
from core.views.customdatatable import CustomDatatable, Colonne
from core.views import crud, liste_questionnaires_base


class Page(crud.Page):
    model = QuestionnaireReponse
    template_name = "individus/edition_questionnaires.html"
    url_liste = "questionnaires_individus_liste"
    description_liste = "Voici ci-dessous la liste des réponses en fonction de la question selectionnée. ATTENTION, si vous modifiez une valeur, vous ne pourrez pas revenir en arrière. N'hésitez pas à filtrer pour vous simplifier la modification."


class Liste(Page, liste_questionnaires_base.Liste):
    template_name = "individus/edition_questionnaires.html"
    categorie_question = "individu"
    filtres = ["ipresent:individu", "iscolarise:individu", "individu__nom", "individu__prenom"]
    colonnes = [
        Colonne(code="individu__nom", label="Nom", classe="CharField", label_filtre="Nom"),
        Colonne(code="individu__prenom", label="Prénom", classe="CharField", label_filtre="Prénom"),
    ]

    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['page_titre'] = "Questionnaires"
        context['box_titre'] = "Modification groupée des réponses aux questionnaires"
        return context

    def Get_customdatatable(self):
        lignes = []
        question_id = self.kwargs.get("categorie", None)
        question = QuestionnaireQuestion.objects.get(pk=question_id) if question_id else None

        if question:
            if question.controle in ("ligne_texte", "bloc_texte", "liste_deroulante", "liste_coches"):
                classe = "CharField"
            elif question.controle in ("entier", "slider"):
                classe = "IntegerField"
            elif question.controle in ("decimal", "montant"):
                classe = "DecimalField"
            elif question.controle == "case_coche":
                classe = "BooleanField"

            # Ajouter une colonne pour la réponse modifiable
            colonne_reponse_editable = Colonne(code="reponse_editable", label="Modifier Réponse", classe=classe, label_filtre="Modifier Réponse")
            colonnes = self.colonnes + [colonne_reponse_editable]
        else :
            colonnes = self.colonnes
        for reponse in QuestionnaireReponse.objects.select_related("question", "individu").filter(Q(question=self.Get_categorie()) & self.Get_filtres("Q")):
            # Formatez la réponse pour l'affichage
            formatted_reponse = self.Formate_reponse(reponse.Get_reponse_fr())
            # Ajoutez un champ de formulaire basé sur le type de réponse
            if classe == "CharField":
                editable_field = f"<input type='text' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"
            elif classe == "IntegerField":
                editable_field = f"<input type='number' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"
            elif classe == "DecimalField":
                editable_field = f"<input type='number' step='0.01' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"
            elif classe == "BooleanField":
                checked = "checked" if formatted_reponse.lower() == "oui" else ""
                editable_field = f"<input type='checkbox' name='reponse_{reponse.pk}' {checked} />"
            else:
                editable_field = formatted_reponse

            lignes.append([
                reponse.individu.nom,
                reponse.individu.prenom,
                editable_field,
            ])

        return CustomDatatable(colonnes=colonnes, lignes=lignes)
