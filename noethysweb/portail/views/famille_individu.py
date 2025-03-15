from django import forms
from core.models import Individu, Famille, Rattachement
from django.shortcuts import render
from core.utils import utils_questionnaires
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import logging

from portail.views.base import CustomView
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class View(CustomView, TemplateView):
    menu_code = "portail_renseignements"
    template_name = "portail/famille_individu.html"

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context["page_titre"] = _("Ajouter un enfant")
        context["famille"] = Famille.objects.prefetch_related("nom").filter(
            nom=self.request.user.famille,
        )
        return context


class IndividuForm(forms.ModelForm):
    date_naiss = forms.DateField(
        required=True, widget=forms.DateInput(attrs={"type": "date"})
    )
    prenom = forms.CharField(max_length=200, required=True)

    class Meta:
        model = Individu
        fields = ["prenom", "nom", "date_naiss"]

    def save_individu(self, famille):
        # Sauvegarde de l'objet Individu en base de données
        individu = super().save(commit=False)
        individu.statut = "5"
        individu.save()

        categorie = "2"
        titulaire = True
        # Création des questionnaires de type individu
        utils_questionnaires.Creation_reponses(
            categorie="individu", liste_instances=[individu]
        )

        # Recherche d'une adresse à rattacher
        rattachements = Rattachement.objects.prefetch_related("individu").filter(
            famille=famille
        )
        for rattachement in rattachements:
            if rattachement.individu.adresse_auto is None:
                individu.adresse_auto = rattachement.individu.pk
                individu.save()
                # Sauvegarde du rattachement
                rattachement = Rattachement(
                    famille=famille,
                    individu=individu,
                    categorie=categorie,
                    titulaire=titulaire,
                )
                rattachement.save()
                individu.Maj_infos()
                break
        return individu


def get_context_data(self, **kwargs):
    context = super(View, self).get_context_data(**kwargs)
    context["famille"] = Famille.objects.prefetch_related("nom").filter(
        nom=self.request.user.famille,
    )
    return context


@login_required
def ajout(request):
    if request.method == "POST":
        form = IndividuForm(request.POST)
        logger.debug(f"Données soumises: {request.POST}")
        if form.is_valid():
            famille = request.user.famille
            logger.debug(f"Famille: {famille}")
            individu = form.save_individu(famille)
            logger.debug(f"Individu enregistré: {individu}")
            return HttpResponseRedirect(reverse("portail_renseignements"))
    else:
        form = IndividuForm()
    return render(request, "portail/famille_individu.html", {"form": form})
