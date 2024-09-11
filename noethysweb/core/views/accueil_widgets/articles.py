import logging, datetime, random
from django.core.cache import cache
from core.views import accueil_widget
from core.utils import utils_parametres
import datetime
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.db.models import Q
from portail.views.base import CustomView
from portail.utils import utils_approbations
from individus.utils import utils_pieces_manquantes, utils_vaccinations, utils_assurances
from cotisations.utils import utils_cotisations_manquantes
from core.models import PortailMessage, Article, Inscription, Consommation, Lecture

class Widget(accueil_widget.Widget):
    code = "articles"
    label = "Articles publiés"
    template_name = "widgets/articles.html"

    def init_context_data(self):
        articles, articles_popups = self.Get_articles()  # Récupération des deux valeurs
        self.context['articles'] = articles  # Ajout des articles dans le contexte
        self.context['articles_popups'] = articles_popups

    def Get_articles(self):
        # Obtenez les structures associées à l'utilisateur (self.request.user)
        structures = self.request.user.structures.all()

        # Définissez les conditions pour les articles publiés
        conditions = Q(statut="publie") & Q(date_debut__lte=datetime.datetime.now()) & (
            Q(date_fin__isnull=True) | Q(date_fin__gte=datetime.datetime.now()))
        conditions &= (Q(public__in=("toutes", "presents", "presents_groupes")) |
                       (Q(public="inscrits") & Q(activites__structure__in=structures)))

        # Récupérer les articles correspondant aux conditions
        articles = Article.objects.select_related("image_article", "album", "sondage", "auteur").filter(
            conditions).distinct().order_by("-date_debut")
        # Sélectionner les articles valides et les popups
        selection_articles = []
        popups = []
        for article in articles:
            # Vérifiez les conditions spécifiques pour les articles avec "presents" et "presents_groupes"
            if article.public in ("presents", "presents_groupes"):
                conditions = Q(date__gte=article.present_debut,
                               date__lte=article.present_fin, etat__in=("reservation", "present"))
                if article.public == "presents":
                    conditions &= Q(activite__in=article.activites.all())
                if article.public == "presents_groupes":
                    conditions &= Q(groupe__in=article.groupes.all())

                # Validez si l'article peut être affiché
                valide = Consommation.objects.filter(conditions).exists()
            else:
                valide = True

            # Ajouter l'article à la liste si valide
            if valide:
                selection_articles.append(article)
        # Retourne les articles et les popups (si nécessaire)
        return selection_articles, popups
