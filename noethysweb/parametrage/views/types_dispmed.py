# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy, reverse
from django.db.models import Count
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.utils import utils_dates
from core.models import TypeDispmed
from parametrage.forms.types_dispmed import Formulaire


class Page(crud.Page):
    model = TypeDispmed
    url_liste = "types_dispmed_liste"
    url_ajouter = "types_dispmed_ajouter"
    url_modifier = "types_dispmed_modifier"
    url_supprimer = "types_dispmed_supprimer"
    description_liste = "Voici ci-dessous la liste des dispositifs médicaux."
    description_saisie = "Saisissez toutes les informations concernant le dispositif médical à saisir et cliquez sur le bouton Enregistrer."
    objet_singulier = "un dispositif médical"
    objet_pluriel = "des dispositifs médicaux"
    boutons_liste = [
        {"label": "Ajouter", "classe": "btn btn-success", "href": reverse_lazy(url_ajouter), "icone": "fa fa-plus"},
    ]


class Liste(Page, crud.Liste):
    model = TypeDispmed

    def get_queryset(self):
        return TypeDispmed.objects.filter(self.Get_filtres("Q")).annotate(nbre_individus=Count('individu_dispmed'))

    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['impression_introduction'] = ""
        context['impression_conclusion'] = ""
        context['afficher_menu_brothers'] = True
        return context

    class datatable_class(MyDatatable):
        filtres = ["idtype_dispmed", "nom"]
        actions = columns.TextColumn("Actions", sources=None, processor='Get_actions_standard')
        nbre_individus = columns.TextColumn("Individus associés", sources="nbre_individus")

        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ["idtype_dispmed", "nom", "nbre_individus"]
            ordering = ["nom"]
            processors = {
            }


class Ajouter(Page, crud.Ajouter):
    form_class = Formulaire

class Modifier(Page, crud.Modifier):
    form_class = Formulaire

class Supprimer(Page, crud.Supprimer):
    manytomany_associes = [
        ("individu(s)", "individu_dispmed"),
    ]
