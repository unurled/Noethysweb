# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.db.models import Q
from core.models import QuestionnaireReponse, QuestionnaireQuestion, Activite, Inscription, Individu
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
        activite_question = question.activite
        if activite_question is None:
            activites_accessibles = Activite.objects.filter(structure__in=self.request.user.structures.all())
        else:
            activites_accessibles = Activite.objects.filter(idactivite=activite_question.pk)
        inscriptions_accessibles = Inscription.objects.filter(activite__in=activites_accessibles)
        individus_inscrits = Individu.objects.filter(idindividu__in=inscriptions_accessibles.values('individu'))
        # Définition des classes de champ en fonction du contrôle
        controle_to_classe = {
            "ligne_texte": "CharField",
            "bloc_texte": "CharField",
            "liste_deroulante": "CharField",
            "entier": "IntegerField",
            "slider": "IntegerField",
            "decimal": "DecimalField",
            "montant": "DecimalField",
            "case_coche": "BooleanField",
            "liste_coches": "BooleanField2"
        }

        classe = controle_to_classe.get(question.controle) if question else None

        # Ajout de la colonne de réponse éditable si une question est sélectionnée
        colonnes = self.colonnes[:]
        if classe:
            colonnes.append(Colonne(code="reponse_editable", label="Modifier Réponse", classe=classe,
                                    label_filtre="Modifier Réponse"))

        # Filtrage des réponses en fonction de la catégorie et des filtres
        reponses = QuestionnaireReponse.objects.select_related("question", "individu").filter(
            Q(question=self.Get_categorie(),individu__in=individus_inscrits) &  self.Get_filtres("Q")
        )

        for reponse in reponses:
            formatted_reponse = self.Formate_reponse(reponse.Get_reponse_fr())

            # Génération des champs éditables
            if classe == "CharField":
                editable_field = f"<input type='text' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"

            elif classe == "IntegerField":
                editable_field = f"<input type='number' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"

            elif classe == "DecimalField":
                editable_field = f"<input type='number' step='0.01' name='reponse_{reponse.pk}' value='{formatted_reponse}' />"

            elif classe == "BooleanField":
                option_label = question.label
                checked = "checked" if "oui" in formatted_reponse.lower() else ""
                editable_field = f"<label><input type='checkbox' name='reponse_{reponse.pk}' {checked} /> {option_label}</label>"

            elif classe == "BooleanField2":
                options_disponibles = [opt.strip() for opt in question.choix.split(";") if opt.strip()]
                reponses_cochees = [opt.strip().lower() for opt in formatted_reponse.split(",")]
                editable_field = ""

                for option in options_disponibles:
                    checked = "checked" if option.lower() in reponses_cochees else ""
                    editable_field += f"<label><input type='checkbox' name='reponse_{reponse.pk}_{option}' {checked} /> {option}</label><br>"

            else:
                editable_field = formatted_reponse

            lignes.append([
                reponse.individu.nom,
                reponse.individu.prenom,
                editable_field,
            ])

        return CustomDatatable(colonnes=colonnes, lignes=lignes)
