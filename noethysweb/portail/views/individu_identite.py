# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from portail.views.fiche import Onglet, ConsulterBase
from portail.forms.individu_identite import Formulaire


class Consulter(Onglet, ConsulterBase):
    form_class = Formulaire
    template_name = "portail/fiche_edit.html"
    mode = "CONSULTATION"
    onglet_actif = "individu_identite"
    categorie = "individu_identite"
    titre_historique = "Modifier l'identité"

    def get_context_data(self, **kwargs):
        context = super(Consulter, self).get_context_data(**kwargs)
        context['box_titre'] = _("Identité")
        context['box_introduction'] = _("Cliquez sur le bouton Modifier au bas de la page pour modifier une des informations ci-dessous.")
        context['onglet_actif'] = self.onglet_actif
        return context

    def get_object(self):
        return self.get_individu()


class Modifier(Consulter):
    mode = "EDITION"

    def get_context_data(self, **kwargs):
        context = super(Modifier, self).get_context_data(**kwargs)
        context['box_introduction'] = _("Renseignez les informations concernant l'identité de l'individu et cliquez sur le bouton Enregistrer.")
        if not self.get_dict_onglet_actif().validation_auto:
            context['box_introduction'] += " " + _("Ces informations devront être validées par l'administrateur de l'application.")
        
        # Détection des champs manquants pour mise en évidence
        individu = self.get_individu()
        champs_manquants = []
        if not individu.civilite:
            champs_manquants.append('civilite')
        if not individu.date_naiss:
            champs_manquants.append('date_naiss')
        if not individu.cp_naiss:
            champs_manquants.append('cp_naiss')
        if not individu.ville_naiss:
            champs_manquants.append('ville_naiss')
        if not individu.nom:
            champs_manquants.append('nom')
        if not individu.prenom:
            champs_manquants.append('prenom')

        context['champs_manquants'] = champs_manquants
        
        return context

    def get_success_url(self):
        self.Maj_infos_famille()
        return reverse_lazy("portail_individu_identite", kwargs={'idrattachement': self.kwargs['idrattachement']})
