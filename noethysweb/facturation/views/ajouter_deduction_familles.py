from django.urls import reverse
from core.views import crud
from core.views.mydatatableview import MyDatatable, columns, helpers
from core.models import Activite, Prestation, Individu
from django.db.models import Q, Sum
from decimal import Decimal
from core.utils import utils_texte


class Page(crud.Page):
    model = Prestation
    menu_code = "liste_deductions"

class Liste(Page, crud.Liste):
    model = Prestation
    
    def get_queryset(self):
        user = self.request.user
        
        activite_ids = Activite.objects.filter(structure__in=user.structures.all(),visible=True).values_list('idactivite', flat=True)
        return Prestation.objects.select_related("individu", "activite", "activite__structure", "facture").annotate(ventile=Sum("ventilation__montant")).filter(Q(activite__in=activite_ids) & self.Get_filtres("Q"))
    
    def get_context_data(self, **kwargs):
        context = super(Liste, self).get_context_data(**kwargs)
        context['page_titre'] = "Ajouter une déduction"
        context['box_titre'] = "Sélection de la prestation"
        context['box_introduction'] = "Recherchez et sélectionnez la prestation pour laquelle vous souhaitez ajouter une déduction. Cliquez ensuite sur le +."
        return context
    
    class datatable_class(MyDatatable):
        filtres = ['idprestation', 'date', 'individu__nom', 'activite__nom', 'label', 'montant']
        facture = columns.TextColumn("Facture", sources=["facture__numero"])
        activite = columns.TextColumn("Activité", sources=['activite__nom'])
        label = columns.TextColumn("Label", sources=['label'])
        individu = columns.TextColumn("Individu", sources=["individu__nom", "individu__prenom"],processor="Formate_individu")
        montant = columns.TextColumn("Montant", sources=["montant"], processor='Formate_montant')
        actions = columns.TextColumn("Ajouter une déduction", sources=None, processor='Get_actions_speciales')

        class Meta:
            structure_template = MyDatatable.structure_template
            columns = ['idprestation', 'date', 'individu', 'activite', 'label', 'montant', 'facture']
            processors = {
                'date': helpers.format_date('%d/%m/%Y'),
                'montant': "Formate_montant_standard",
            }
            ordering = ['individu']

        def Formate_montant(self, instance, **kwargs):
            ventile = Decimal(instance.ventile or 0.0)
            if ventile == Decimal(0):
                classe = "text-red"
                title = "Prestation impayée"
            elif ventile == instance.montant:
                classe = "text-green"
                title = "Prestation totalement payée"
            else:
                classe = "text-orange"
                title = "Prestation partiellement payée (%s)" % utils_texte.Formate_montant(ventile)
            return "<span title='%s' class='%s'>%s</span>" % (title, classe, utils_texte.Formate_montant(instance.montant))

        def Formate_individu(self, instance, **kwargs):
            return instance.individu.Get_nom() if instance.individu else ""
        
        def Get_actions_speciales(self, instance, *args, **kwargs):
            html = [
                self.Create_bouton_ajouter(url=reverse("famille_prestations_modifier", kwargs={"pk": instance.idprestation, "idfamille": instance.famille.pk}), title="Ajouter une déduction")
            ]
            return self.Create_boutons_actions(html)