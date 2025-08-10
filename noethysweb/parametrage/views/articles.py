from django.urls import reverse_lazy, reverse
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.views import crud
from core.models import Article
from parametrage.forms.articles import Formulaire
from copy import deepcopy

class Page(crud.Page):
    model = Article
    url_liste = "articles_liste"
    url_ajouter = "articles_ajouter"
    url_modifier = "articles_modifier"
    url_supprimer = "articles_supprimer"
    url_dupliquer = "articles_dupliquer"
    description_liste = "Voici ci-dessous la liste des articles à afficher sur le portail."
    description_saisie = "Saisissez toutes les informations concernant l'article et cliquez sur le bouton Enregistrer."
    objet_singulier = "un article"
    objet_pluriel = "des articles"
    boutons_liste = [
        {"label": "Ajouter", "classe": "btn btn-success", "href": reverse_lazy(url_ajouter), "icone": "fa fa-plus"},
    ]

class Liste(Page, crud.Liste):
    model = Article

    def get_queryset(self):
        if self.request.user.is_staff:
            return Article.objects.filter(self.Get_filtres("Q"), self.Get_condition_structure())
        return Article.objects.filter(self.Get_filtres("Q"), self.Get_condition_structure(), auteur=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['impression_introduction'] = ""
        context['impression_conclusion'] = ""
        context['afficher_menu_brothers'] = True
        return context

    class datatable_class(MyDatatable):
        filtres = ["idarticle", "titre", "date_debut", "date_fin"]
        actions = columns.TextColumn("Actions", sources=None, processor='Get_actions_speciales')
        statut = columns.TextColumn("Statut", sources=["statut"], processor='Get_statut')

        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ["idarticle", "titre", "date_debut", "date_fin", "statut"]
            ordering = ["date_debut"]
            processors = {
                "date_debut": helpers.format_date("%d/%m/%Y %H:%M"),
                "date_fin": helpers.format_date("%d/%m/%Y %H:%M"),
                "statut": "Get_statut",
            }

        def Get_statut(self, instance, *args, **kwargs):
            if instance.statut == "publie":
                return "<small class='badge badge-success'>Publié</small>"
            else:
                return "<small class='badge badge-danger'>Non publié</small>"

        def Get_actions_speciales(self, instance, *args, **kwargs):
            html = [
                self.Create_bouton_modifier(url=reverse(kwargs["view"].url_modifier, args=[instance.pk])),
                self.Create_bouton_supprimer(url=reverse(kwargs["view"].url_supprimer, args=[instance.pk])),
                self.Create_bouton_dupliquer(url=reverse(kwargs["view"].url_dupliquer, args=[instance.pk])),
            ]
            return self.Create_boutons_actions(html)

class Ajouter(Page, crud.Ajouter):
    form_class = Formulaire

class Modifier(Page, crud.Modifier):
    form_class = Formulaire

class Supprimer(Page, crud.Supprimer):
    pass

class Dupliquer(Page, crud.Dupliquer):
    def post(self, request, **kwargs):
        # Récupération de l'article à dupliquer
        article_id = kwargs.get('pk')
        article = Article.objects.get(pk=article_id)

        # Duplication de l'article
        nouvel_article = deepcopy(article)
        nouvel_article.pk = None
        nouvel_article.titre = "Copie de %s" % article.titre
        nouvel_article.save()

        # Redirection vers l'article dupliqué
        if "dupliquer_ouvrir" in request.POST:
            url = reverse(self.url_modifier, args=[nouvel_article.pk])
        else:
            url = reverse(self.url_liste)  # Redirection vers la liste d'articles après la duplication

        return self.Redirection(url=url)
