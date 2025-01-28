# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.
import logging
logger = logging.getLogger(__name__)
import datetime, decimal
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Inscription, Activite, Groupe, Rattachement, Cotisation, Prestation, Ventilation, Tarif, Individu, CategorieTarif, TarifLigne
from core.utils import utils_texte
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect




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
        context["impression_conclusion"] = ""
        context["afficher_menu_brothers"] = True
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
        if self.Get_activite():
            context['liste_groupes'] = [
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
            structure_template = MyDatatable.structure_template
            columns = ["check", "id", "individu", "famille"]
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

    # Fonction de vérification des inscriptions existantes
def check_inscriptions_existantes(request, activite, individu, famille, instance=None):
    activite_f = Activite.objects.get(idactivite=activite)
    if not activite_f.inscriptions_multiples:
        date_debut = datetime.date.today()
        date_fin = datetime.date(2999, 12, 31)
        inscriptions_paralleles = []

        # On filtre les inscriptions existantes pour cet individu, famille, et activité
        for inscription in Inscription.objects.filter(
                individu=individu,
                famille=famille,
                activite=activite):
                # Si l'inscription est différente de l'instance actuelle, on la considère comme parallèle
                if inscription != instance:
                    inscriptions_paralleles.append(inscription)

        # Si des inscriptions parallèles existent, on affiche un message d'erreur
        if inscriptions_paralleles:
            return False
    return True

# Vue pour gérer l'inscription en lot
def lancer_inscriptions(request, activite, groupe, tarif, listepk):
    # Affichage de débogage pour vérifier les valeurs
    tarif_f=tarif
    if ',' in listepk:
        liste_ids = listepk.split(',')  # Décomposer la chaîne en plusieurs IDs
    else:
        liste_ids = [listepk]

    # Pour chaque ID dans la liste listepk, effectuer les actions suivantes
    for pk in liste_ids:
        try:
            individu = Individu.objects.get(idindividu=pk)
            ratt = Rattachement.objects.get(individu=individu)
            famille = ratt.famille
        except Individu.DoesNotExist:
            messages.add_message(request, messages.ERROR, f"Merci de selectionner au moins un individu et un groupe.")
            continue  # Passer à l'élément suivant de la liste

        # Vérification des inscriptions existantes
        if not check_inscriptions_existantes(request=request, activite=activite, individu=individu, famille=famille):
            messages.add_message(request, messages.ERROR, f"{individu} est déjà inscrit à cette activité. Veuillez plutôt modifier l'inscription")
            continue

        premiere_categorie = CategorieTarif.objects.filter(activite=activite).order_by('idcategorie_tarif').first()
        if not premiere_categorie:
            messages.add_message(request, messages.ERROR, "Aucune catégorie tarifaire trouvée pour cette activité.")
            continue

        logger.debug(f"Création de l'inscription pour {individu} dans l'activité {activite}")
        activite_f = Activite.objects.get(idactivite=activite)
        groupe_f = Groupe.objects.get(idgroupe=groupe)

        # Crée l'inscription pour cet individu
        inscription = Inscription.objects.create(
            activite=activite_f,
            famille=famille,
            groupe=groupe_f,
            individu=individu,
            categorie_tarif=premiere_categorie,
            internet_reservations=1,
            statut="ok",
            date_debut=datetime.date.today()
        )
        logger.debug(f"Inscription créée : {inscription}")

        #Création ET modification prestations !!!! La modif est bloqué pas plus haut la vérif d'une iscription existante mais dans la théorie on modifie la prestation et pas seulement la crée
        if ',' in tarif_f:
            liste_tarif = tarif_f.split(',')  # Décomposer la chaîne en plusieurs IDs
        else:
            liste_tarif = [tarif_f]

        # Récupérer les objets Tarif correspondants
        tarifs_objects = Tarif.objects.filter(pk__in=liste_tarif )

        # Récupérer les descriptions correspondantes depuis la base de données
        descriptions_tarifs = Tarif.objects.filter(pk__in=liste_tarif).values_list('description', flat=True)

        # Récupérer les objets Tarif correspondants aux descriptions
        tarifs_objects = Tarif.objects.filter(description__in=descriptions_tarifs)
        tarifs_selectionnes = tarifs_objects.filter(pk__in=liste_tarif)

        # Récupérer les tarifs associés aux prestations existantes pour cette inscription
        tarifs_prestations_existants = Prestation.objects.filter(
            individu=individu,
            famille=famille,
            activite=activite,
        ).values_list('tarif', flat=True)

        # Comparer les tarifs sélectionnés avec ceux des prestations existantes
        # Supprimer les tarifs en trop
        for tarif_prestation_existant in tarifs_prestations_existants:
            if tarif_prestation_existant not in tarifs_selectionnes:
                # Supprimer les prestations associées au tarif
                Prestation.objects.filter(
                    tarif=tarif_prestation_existant,
                    individu=individu,
                    famille=famille,
                    activite=activite,
                ).delete()

            # Créer une prestation pour chaque tarif
        for tarif in tarifs_selectionnes:
                if tarif not in tarifs_prestations_existants:
                    tarif_ligne = TarifLigne.objects.get(tarif_id=tarif.pk)
                    montant_unique = tarif_ligne.montant_unique
                    nouvelle_prestation = Prestation.objects.create(
                        date=datetime.date.today(),
                        categorie="consommation",
                        label=tarif.description,
                        forfait=1,
                        montant_initial=montant_unique, #fonctionne pas à chercher dans tarifs_lignes
                        montant=montant_unique, #fonctionne pas a chercher dans tarifs_lignes
                        quantite=1,
                        tva=0,
                        date_valeur=datetime.date.today(),
                        activite=activite_f,
                        categorie_tarif=premiere_categorie,
                        famille=famille,
                        individu=individu,
                        tarif=tarif
                    )
        logger.debug(f"Prestation créée : {individu}")
        messages.add_message(request, messages.SUCCESS, f"L'inscription a bien été enregistrée pour {individu}")

    # Redirection à la fin de la boucle
    url_liste = reverse("inscriptions_activite_lot")  # Utiliser le nom de l'URL de la liste
    return HttpResponseRedirect(url_liste)



