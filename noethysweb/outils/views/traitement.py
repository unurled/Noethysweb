# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy, reverse
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Traitement, Activite, Structure
from outils.forms.traitement import Formulaire

class Page(crud.Page):
    model = Traitement
    url_liste = "traitement_liste"
    url_ajouter = "traitement_ajouter"
    url_modifier = "traitement_modifier"
    url_supprimer = "traitement_supprimer"
    description_liste = "Voici ci-dessous la liste des traitements."
    description_saisie = "Saisissez toutes les informations concernant le traitement à saisir et cliquez sur le bouton Enregistrer."
    objet_singulier = "un traitement"
    objet_pluriel = "des traitements"
    boutons_liste = [
        {"label": "Ajouter", "classe": "btn btn-success", "href": reverse_lazy(url_ajouter), "icone": "fa fa-plus"},
    ]

class Liste(Page, crud.Liste):
    model = Traitement

    def get_queryset(self):
        # Récupère les activités associées à cette structure
        activites_accessibles = Activite.objects.filter(structure__in=self.request.user.structures.all())

        # Filtre les traitements en fonction des activités accessibles par la structure de l'utilisateur
        return Traitement.objects.filter(activite__in=activites_accessibles).filter(self.Get_filtres("Q"))

    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['impression_introduction'] = ""
        context['impression_conclusion'] = ""
        context['afficher_menu_brothers'] = True
        return context

    class datatable_class(MyDatatable):
        filtres = ["date","activite__nom"]
        actions = columns.TextColumn("Actions", sources=None, processor='Get_actions_standard')


        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ["date", "titre","individu","activite",'Description']
            ordering = ["date"]


class Ajouter(Page, crud.Ajouter):
    form_class = Formulaire

class Modifier(Page, crud.Modifier):
    form_class = Formulaire

class Supprimer(Page, crud.Supprimer):
    pass
