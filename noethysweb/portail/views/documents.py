# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import logging
from django.db.models import Q
logger = logging.getLogger(__name__)
from portail.views.base import CustomView
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from individus.utils import utils_pieces_manquantes
from portail.utils import utils_approbations
from core.models import PortailDocument, Inscription, Attestationdoc
from core.utils import utils_dates
from django.http import FileResponse, Http404
from django.conf import settings
import os
import shutil

def imprimer_attestation(request):
    attestation = int(request.POST.get("idattestation", 0))
    idattestationdoc = Attestationdoc.objects.get(idattestation=attestation)
    print(idattestationdoc)
    chemin_relatif_fichier = idattestationdoc.fichier
    fichier_chemin = os.path.join(settings.MEDIA_ROOT, chemin_relatif_fichier)
    print(fichier_chemin)
    response = FileResponse(open(fichier_chemin, 'rb'), as_attachment=True, filename=fichier_chemin)
    return response

class View(CustomView, TemplateView):
    menu_code = "portail_documents"
    template_name = "portail/documents.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context['page_titre'] = _("Documents")

        # Pièces à fournir
        context['pieces_fournir'] = utils_pieces_manquantes.Get_pieces_manquantes(famille=self.request.user.famille, exclure_individus=self.request.user.famille.individus_masques.all())

        # Récupération des activités de la famille
        conditions = Q(famille=self.request.user.famille)
        inscriptions = Inscription.objects.select_related("activite", "individu").filter(conditions)
        activites = list({inscription.activite for inscription in inscriptions})

        # Importation des documents à télécharger
        liste_documents = []
        documents = PortailDocument.objects.filter(Q(activites__in=activites)).order_by("titre").distinct()
        for document in documents:
            liste_documents.append({
                "titre": document.titre,
                "texte": document.texte,
                "fichier": document.document,
                "couleur_fond": document.couleur_fond,
                "extension": document.Get_extension()
            })
        for unite_consentement in utils_approbations.Get_approbations_requises(famille=self.request.user.famille, avec_consentements_existants=False).get("consentements", []):
            liste_documents.append({
                "titre": unite_consentement.type_consentement.nom,
                "texte": "Version du %s" % utils_dates.ConvertDateToFR(unite_consentement.date_debut),
                "fichier": unite_consentement.document,
                "couleur_fond": "primary",
                "extension": unite_consentement.Get_extension()
            })
        context['liste_documents'] = liste_documents

        famille = self.request.user.famille
        attestations = Attestationdoc.objects.filter(famille=famille)
        context['liste_attestations'] = attestations

        return context
