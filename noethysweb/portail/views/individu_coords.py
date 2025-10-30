# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from portail.views.fiche import Onglet, ConsulterBase
from portail.forms.individu_coords import Formulaire


class Consulter(Onglet, ConsulterBase):
    form_class = Formulaire
    template_name = "portail/fiche_edit.html"
    mode = "CONSULTATION"
    onglet_actif = "individu_coords"
    categorie = "individu_coords"
    titre_historique = _("Modifier les coordonnées")

    def get_context_data(self, **kwargs):
        context = super(Consulter, self).get_context_data(**kwargs)
        context['box_titre'] = _("Coordonnées")
        context['box_introduction'] = _("Cliquez sur le bouton Modifier au bas de la page pour modifier une des informations ci-dessous.")
        context['onglet_actif'] = self.onglet_actif
        return context

    def get_object(self):
        return self.get_individu()



class Modifier(Consulter):
    mode = "EDITION"

    def get_context_data(self, **kwargs):
        context = super(Modifier, self).get_context_data(**kwargs)
        context['box_introduction'] = _("Renseignez les informations concernant les coordonnées de l'individu et cliquez sur le bouton Enregistrer.")
        if not self.get_dict_onglet_actif().validation_auto:
            context['box_introduction'] += " " + _("Ces informations devront être validées par l'administrateur de l'application.")
        
        # Détection des champs manquants pour mise en évidence
        individu = self.get_individu()
        rattachement = self.get_rattachement()
        champs_manquants = []
        
        # Vérifier si c'est un parent (titulaire ou représentant)
        if rattachement and (rattachement.titulaire or rattachement.categorie == 1):
            if not individu.rue_resid:
                champs_manquants.append('rue_resid')
            if not individu.cp_resid:
                champs_manquants.append('cp_resid')
            if not individu.ville_resid:
                champs_manquants.append('ville_resid')
            if not individu.tel_mobile and not individu.tel_domicile:
                champs_manquants.append('tel_mobile')
                champs_manquants.append('tel_domicile')
            if not individu.mail:
                champs_manquants.append('mail')
        
        context['champs_manquants'] = champs_manquants
        
        return context

    def get_success_url(self):
        self.Maj_infos_famille()
        return reverse_lazy("portail_individu_coords", kwargs={'idrattachement': self.kwargs['idrattachement']})
