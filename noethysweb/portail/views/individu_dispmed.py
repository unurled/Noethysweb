# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.translation import gettext as _
from portail.views.fiche import Onglet, ConsulterBase
from portail.forms.individu_dispmed import Formulaire
from core.models import TypeDispmed


def Ajouter_dispmed(request):
    """ Ajouter un type de maladie """
    nom = request.POST.get("valeur")
    dispmeds = TypeDispmed.objects.create(nom=nom)
    return JsonResponse({"id": dispmeds.pk, "valeur": dispmeds.nom})

class Consulter(Onglet, ConsulterBase):
    form_class = Formulaire
    template_name = "portail/fiche_edit.html"
    mode = "CONSULTATION"
    onglet_actif = "individu_dispmed"
    categorie = "individu_dispmed"
    titre_historique = _("Modifier les dispositifs médicaux")

    def get_context_data(self, **kwargs):
        context = super(Consulter, self).get_context_data(**kwargs)
        context['box_titre'] = _("Dispositifs médicaux")
        context['box_introduction'] = _("Précisez si votre enfant porte des prothèses dentaire, auditives, lunettes, lentilles...")
        context['onglet_actif'] = self.onglet_actif
        return context

    def get_object(self):
        return self.get_individu()


class Modifier(Consulter):
    mode = "EDITION"

    def get_context_data(self, **kwargs):
        context = super(Modifier, self).get_context_data(**kwargs)
        context['box_introduction'] = _("Sélectionnez un ou plusieurs dispositif médical dans le champ ci-dessous et cliquez sur le bouton Enregistrer.")
        if not self.get_dict_onglet_actif().validation_auto:
            context['box_introduction'] += " " + _("Ces informations devront être validées par l'administrateur de l'application.")
        return context

    def get_success_url(self):
        return reverse_lazy("portail_individu_dispmed", kwargs={'idrattachement': self.kwargs['idrattachement']})
