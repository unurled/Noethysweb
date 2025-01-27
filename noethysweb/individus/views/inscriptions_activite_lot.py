# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import datetime, decimal
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Inscription, Activite, Groupe, Rattachement, Cotisation, Prestation, Ventilation, Tarif, Individu
from core.utils import utils_texte


class Page(crud.Page):
    model = Inscription
    url_liste = "inscriptions_activite_lot"
    description_liste = "Sélectionnez une activité et un groupe, puis cochez les familles souhaitées et cliquez sur le bouton 'Inscrire en lot'."
    objet_singulier = "une inscription"
    objet_pluriel = "des inscriptions"


class Liste(Page, crud.Liste):
    template_name = "individus/inscriptions_activite_lot.html"
    model = Inscription

    def get_queryset(self):
        activites_autorisees = Activite.objects.filter(structure__in=self.request.user.structures.all())
        return Rattachement.objects.select_related("famille", "individu").filter(individu__inscription__activite__in=activites_autorisees).filter(self.Get_filtres("Q"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_checkbox"] = True
        context["bouton_supprimer"] = False
        context['box_titre'] = "Créer des inscriptions en lot"
        context["impression_titre"] = Activite.objects.get(pk=self.Get_activite()).nom if self.Get_activite() else ""
        context["impression_introduction"] = Groupe.objects.get(pk=self.Get_groupe()).nom if self.Get_groupe() else ""

        # Liste des activités
        condition = Q()
        liste_activites = [
                              (None, "--------")
                          ] + [
                              (
                                  activite.pk,
                                  f"{activite.nom}"
                              )
                              for activite in
                              Activite.objects.filter(self.Get_condition_structure(), condition).order_by("-date_fin",
                                                                                                          "nom")
                          ]
        context['liste_activites'] = liste_activites

        # Liste des groupes
        context['liste_groupes'] = [(None, "Tous les groupes")]
        if self.Get_activite():
            context['liste_groupes'] += [
                (groupe.pk, groupe.nom) for groupe in
                Groupe.objects.filter(activite_id=int(self.Get_activite())).order_by("ordre")
            ]

        # Liste des tarifs
        context['liste_tarifs'] = []
        if self.Get_activite():
            context['liste_tarifs'] += [
                (tarif.pk, tarif.description) for tarif in
                Tarif.objects.filter(activite=int(self.Get_activite()))
            ]

        context['tarifs'] = int(self.Get_tarif()) if self.Get_tarif() else None
        context['groupe'] = int(self.Get_groupe()) if self.Get_groupe() else None
        context['activite'] = int(self.Get_activite()) if self.Get_activite() else None
        return context

    def Get_activite(self):
        activite = self.kwargs.get("activite", None)
        if activite:
            activite = activite.replace("A", "")
            return activite
        return None

    def Get_groupe(self):
        groupe = self.kwargs.get("groupe", None)
        if groupe:
            return int(groupe)
        return None

    def Get_tarif(self):
        tarifs = self.request.GET.getlist("tarif", [])
        return [int(tarif) for tarif in tarifs if tarif.isdigit()]

    class datatable_class(MyDatatable):
        filtres = ["famille__nom", "individu__nom", "individu__prenom"]
        check = columns.CheckBoxSelectColumn(label="")
        id = columns.TextColumn("ID", sources=["individu__idindividu"])
        famille = columns.TextColumn("Famille", sources=["famille__nom"])
        individu = columns.CompoundColumn("Individu", sources=["individu__nom", "individu__prenom"])

        class Meta:
            columns = ["check", "id", "famille", "individu"]
            page_length = 100
            ordering = ["famille"]

        def Init_dict_parents(self):
            # Importation initiale des parents
            if not hasattr(self, "dict_parents"):
                self.dict_parents = {}
                self.liste_enfants = []
                for rattachement in Rattachement.objects.select_related("individu").all():
                    if rattachement.categorie == 1:
                        self.dict_parents.setdefault(rattachement.famille_id, [])
                        self.dict_parents[rattachement.famille_id].append(rattachement.individu)
                    if rattachement.categorie == 2:
                        self.liste_enfants.append((rattachement.famille_id, rattachement.individu_id))

# Vue pour gérer l'inscription en lot
def lancer_inscriptions(request, activite, groupe, tarif, listepk):
    print(activite)
    print(activite)
    print(groupe)
    print(tarif)
    print(listepk)

    # Retourner une réponse ou rediriger
    return render(request, 'votre_template.html', {
        'activite': activite_obj,
        'groupe': groupe_obj,
        'tarifs': tarifs_obj,
        'pks': pk_liste_list
    })