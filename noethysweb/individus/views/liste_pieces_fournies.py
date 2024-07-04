# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import reverse_lazy, reverse
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Piece
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class Page(crud.Page):
    model = Piece
    url_liste = "liste_pieces_fournies"
    description_liste = "Voici ci-dessous la liste des pièces fournies."
    objet_singulier = "une pièce fournie"
    objet_pluriel = "des pièces fournies"
    url_supprimer_plusieurs = "pieces_supprimer_plusieurs"


class Liste(Page, crud.Liste):
    # model = Piece

    def get_queryset(self):
        return Piece.objects.select_related("famille", "individu", "type_piece").filter(self.Get_filtres("Q"))

    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['impression_introduction'] = ""
        context['impression_conclusion'] = ""
        context['active_checkbox'] = True
        return context

    class datatable_class(MyDatatable):
        filtres = ["fpresent:famille", "ipresent:individu", "fscolarise:famille", "iscolarise:individu", "idpiece", "date_debut", "date_fin", "famille__nom", "individu__nom", "type_piece__nom"]
        actions = columns.TextColumn("Actions", sources=None, processor='Get_actions_speciales')
        check = columns.CheckBoxSelectColumn(label="")

        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ['check', "idpiece", "date_debut", "date_fin", "type_piece", "famille", "individu", "actions"]
            processors = {
                'date_debut': helpers.format_date('%d/%m/%Y'),
                'date_fin': helpers.format_date('%d/%m/%Y'),
            }
            ordering = ["date_debut"]

        def Get_actions_speciales(self, instance, *args, **kwargs):
            document_url = f'/media/{instance.document}'

            # Récupération des informations pertinentes pour le titre du document
            type_piece = instance.type_piece.nom if instance.type_piece else ""
            individu = instance.individu.prenom if instance.individu else ""
            famille = instance.individu.nom if instance.famille else ""

            # Construction du titre du document pour le lien de téléchargement
            titre_document = f"{type_piece} - {individu} {famille}"

            # Construction du lien de téléchargement avec l'icône et l'attribut download
            bouton_telecharger = f'<a href="{document_url}" class="btn btn-primary" download="{titre_document}"><i class="fa fa-download"></i></a>'
            bouton_ouvrir = f'<a href="{document_url}" class="btn btn-primary" target="_blank"><i class="fa fa-eye"></i></a>'


            html = [
                bouton_ouvrir,
                bouton_telecharger,
            ]

            return self.Create_boutons_actions(html)

class Supprimer_plusieurs(Page, crud.Supprimer_plusieurs):
    pass
