import logging

from django.http.request import HttpRequest

from core.models import (
    CATEGORIE_RATTACHEMENT_ENFANT,
    Famille,
    Individu,
    Rattachement,
    Utilisateur,
)
from core.utils import utils_questionnaires
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from core.widgets import CodePostal, Ville

logger = logging.getLogger(__name__)


class IndividuForm(forms.ModelForm):
    date_naiss = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    prenom = forms.CharField(max_length=200, required=True)

    class Meta:
        model = Individu
        fields = ["prenom", "nom", "date_naiss", "cp_naiss", "ville_naiss"]
        widgets = {
            "cp_naiss": CodePostal(attrs={"id_ville": "id_ville_naiss"}),
            "ville_naiss": Ville(attrs={"id_codepostal": "id_cp_naiss"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user: Utilisateur = user
        super().__init__(*args, **kwargs)
        print("user", dir(user))
        print(dir(user.famille))

    def save_individu(self, famille: Famille):
        # Sauvegarde de l'objet Individu en base de données
        individu = super().save(commit=False)
        individu.statut = Individu.STATUT_JEUNE
        individu.save()

        # Création des questionnaires de type individu
        utils_questionnaires.Creation_reponses(
            categorie="individu", liste_instances=[individu]
        )

        # Recherche d'une adresse à rattacher
        rattachement_addr = (
            Rattachement.objects.prefetch_related("individu")
            .filter(famille=famille, individu__adresse_auto__isnull=True)
            .first()
        )
        individu.adresse_auto = rattachement_addr.individu.pk
        individu.save()

        # Sauvegarde du rattachement
        rattachement = Rattachement(
            famille=famille,
            individu=individu,
            categorie=CATEGORIE_RATTACHEMENT_ENFANT,
            titulaire=False,
        )
        rattachement.save()
        individu.Maj_infos()

        return individu


@login_required
def ajout(request):
    if request.method == "POST":
        form = IndividuForm(request.POST, user=request.user)
        logger.debug(f"Données soumises: {request.POST}")
        if form.is_valid():
            famille = request.user.famille
            logger.debug(f"Famille: {famille}")
            individu = form.save_individu(famille)
            logger.debug(f"Individu enregistré: {individu}")
            return HttpResponseRedirect(reverse("portail_renseignements"))
    else:
        form = IndividuForm(user=request.user)
    return render(request, "portail/famille_individu.html", {"form": form})
