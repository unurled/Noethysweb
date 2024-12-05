# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Individu, Activite, Structure, Inscription
from fiche_individu.forms.individu_allergies import Formulaire


class Page(crud.Page):
    model = Individu
    url_liste = "allergies_liste"
    url_modifier = "allergies_modifier"
    description_liste = "Voici ci-dessous la liste des allergies des individus."
    description_saisie = "Sélectionnez un ou plusieurs allergies dans la liste proposée et cliquez sur le bouton Enregistrer."
    objet_singulier = "une allergie"
    objet_pluriel = "des allergies"


class Liste(Page, crud.Liste):
    model = Individu

    def get_queryset(self):
        activites_accessibles = Activite.objects.filter(structure__in=self.request.user.structures.all())
        inscriptions_accessibles = Inscription.objects.filter(activite__in=activites_accessibles)
        individus_inscrits = Individu.objects.filter(idindividu__in=inscriptions_accessibles.values('individu'))
        return individus_inscrits.prefetch_related("allergies").filter(allergies__isnull=False,).filter(self.Get_filtres("Q"))

    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['page_titre'] = "Alergies"
        context['box_titre'] = "Liste des allergies"
        return context

    class datatable_class(MyDatatable):
        filtres = ["idindividu", "ipresent:pk", "iscolarise:pk", "nom", "prenom", "maladies__nom"]
        actions = columns.TextColumn("Actions", sources=None, processor='Get_actions_speciales')
        individu = columns.CompoundColumn("Individu", sources=['nom', 'prenom'])
        allergies = columns.TextColumn("Allergies", sources=["allergies__nom"], processor='Get_allergies')

        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ["idindividu", "individu", "allergies", "actions"]
            ordering = ["individu"]

        def Get_allergies(self, instance, *args, **kwargs):
            return ", ".join([allergie.nom for allergie in instance.allergies.all()])

        def Get_actions_speciales(self, instance, *args, **kwargs):
            html = [
                self.Create_bouton_modifier(url=reverse(kwargs["view"].url_modifier, args=[instance.pk])),
            ]
            return self.Create_boutons_actions(html)


class Modifier(Page, crud.Modifier):
    form_class = Formulaire

class Supprimer(Page, crud.Supprimer):
    form_class = Formulaire
