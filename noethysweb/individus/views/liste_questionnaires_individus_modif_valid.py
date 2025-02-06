from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponseBadRequest
from django.contrib import messages
from core.models import QuestionnaireReponse, QuestionnaireQuestion, Activite, Individu, Inscription
from django.db.models import Q


class liste_questionnaires_individus_modif_valid(View):
    def post(self, request, *args, **kwargs):
        nb_reponses_modifiees = 0  # Compteur des réponses réellement modifiées
        checkbox_groups = {}  # Dictionnaire pour stocker les groupes de cases à cocher

        question_id = self.kwargs.get("categorie", None)
        question = QuestionnaireQuestion.objects.get(pk=question_id) if question_id else None
        activite_question = question.activite
        if activite_question is None:
           activites_accessibles = Activite.objects.filter(structure__in=self.request.user.structures.all())
        else:
            activites_accessibles = Activite.objects.filter(idactivite=activite_question.pk)
            inscriptions_accessibles = Inscription.objects.filter(activite__in=activites_accessibles)
            individus_inscrits = Individu.objects.filter(idindividu__in=inscriptions_accessibles.values('individu'))

        reponses = QuestionnaireReponse.objects.select_related("question", "individu").filter(Q(question=question_id,individu__in=individus_inscrits))
        reponse_ids = list(reponses.values_list('idreponse', flat=True))
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

        for reponse in QuestionnaireReponse.objects.filter(idreponse__in=reponse_ids):
            nouvelle_reponse = None  # Initialisation de la nouvelle valeur

            if classe == "CharField":
                nouvelle_reponse = request.POST.get(f"reponse_{reponse.idreponse}", "").strip()

            elif classe == "IntegerField":
                valeur_post = request.POST.get(f"reponse_{reponse.idreponse}", "")
                nouvelle_reponse = int(valeur_post) if valeur_post.isdigit() else None

            elif classe == "DecimalField":
                valeur_post = request.POST.get(f"reponse_{reponse.idreponse}", "").replace(",", ".")
                try:
                    nouvelle_reponse = float(valeur_post) if valeur_post else None
                except ValueError:
                    nouvelle_reponse = None  # Gérer une valeur incorrecte

            elif classe == "BooleanField":
                nouvelle_reponse = f"reponse_{reponse.idreponse}" in request.POST

            elif classe == "BooleanField2":
                options_disponibles = [opt.strip() for opt in reponse.question.choix.split(";") if opt.strip()]

                # Récupérer les options cochées depuis le POST
                reponses_cochees = [
                    option for option in options_disponibles
                    if f"reponse_{reponse.idreponse}_{option}" in request.POST
                ]

                nouvelle_reponse = ", ".join(reponses_cochees)  # Convertir en string pour stockage

            # Comparer avec l'ancienne valeur et sauvegarder si nécessaire
            if nouvelle_reponse is not None and reponse.reponse != nouvelle_reponse:
                reponse.reponse = nouvelle_reponse
                reponse.save()
                nb_reponses_modifiees += 1  # Incrémentation seulement en cas de modification

        # Afficher un message seulement si des réponses ont été modifiées
        if nb_reponses_modifiees > 0:
            messages.add_message(request, messages.SUCCESS, f"Les réponses sont modifiées")

        return redirect('questionnaires_individus_modif', categorie=question_id)
