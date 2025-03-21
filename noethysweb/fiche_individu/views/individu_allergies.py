# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy
from django.http import JsonResponse
from core.views import crud
from core.models import Individu, TypeAllergie
from fiche_individu.forms.individu_allergies import Formulaire
from fiche_individu.views.individu import Onglet


def Ajouter_allergie(request):
    """ Ajouter un type de maladie """
    nom = request.POST.get("valeur")
    allergie = TypeAllergie.objects.create(nom=nom)
    return JsonResponse({"id": allergie.pk, "valeur": allergie.nom})


class Consulter(Onglet, crud.Modifier):
    form_class = Formulaire
    template_name = "fiche_individu/individu_edit.html"
    mode = "CONSULTATION"

    def get_context_data(self, **kwargs):
        context = super(Consulter, self).get_context_data(**kwargs)
        context['box_titre'] = "Allergies"
        context['box_introduction'] = "Cliquez sur le bouton Modifier pour modifier une des informations ci-dessous."
        context['onglet_actif'] = "allergies"
        return context

    def get_object(self):
        return Individu.objects.get(pk=self.kwargs['idindividu'])


class Modifier(Consulter):
    mode = "EDITION"

    def get_context_data(self, **kwargs):
        context = super(Modifier, self).get_context_data(**kwargs)
        context['box_introduction'] = "Sélectionnez dans la liste déroulante les allergies contractées par l'individu."
        return context

    def get_success_url(self):
        # MAJ des infos des familles rattachées
        self.Maj_infos_famille()
        return reverse_lazy("individu_allergies", kwargs={'idindividu': self.kwargs['idindividu'], 'idfamille': self.kwargs.get('idfamille', None)})
