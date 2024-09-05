from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponseBadRequest
from django.contrib import messages  # Importer le module de messages
from core.models import QuestionnaireReponse

class liste_questionnaires_individus_modif_valid(View):
    def post(self, request, *args, **kwargs):
        nb_reponses_modifiees = 0  # Compteur pour les réponses modifiées

        # Traiter les données soumises
        for key, value in request.POST.items():
            if key.startswith('reponse_'):
                reponse_id = key.split('_')[1]
                try:
                    # Mettre à jour la réponse
                    reponse = QuestionnaireReponse.objects.get(pk=reponse_id)
                    reponse.reponse = value
                    reponse.save()
                    nb_reponses_modifiees += 1  # le nombre est pas juste. C'est le nb total et pas le nb modifié...
                except QuestionnaireReponse.DoesNotExist:
                    # Gérer les cas où la réponse n'existe pas
                    return HttpResponseBadRequest("Réponse non trouvée")

        # Ajouter un message de succès avec le nombre de réponses modifiées
        messages.success(request, f"{nb_reponses_modifiees} réponse(s) modifiée(s) avec succès.")

        # Rediriger vers la liste ou une autre vue après la mise à jour
        return redirect('questionnaires_individus_modif')
