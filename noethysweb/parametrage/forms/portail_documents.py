# -*- coding: utf-8 -*-
# Copyright (c) 2019-2021 Ivan LUCAS.
# Noethysweb, application de gestion multi-activités.
# Distribué sous licence GNU GPL.

from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field
from core.forms.base import FormulaireBase
from core.models import PortailDocument, TypePiece, Activite, Groupe
from core.utils import utils_commandes, utils_dates
from core.forms.select2 import Select2MultipleWidget, Select2Widget

class Formulaire(FormulaireBase, forms.ModelForm):
    class Meta:
        model = PortailDocument
        fields = "__all__"
        widgets = {
            "activites": Select2MultipleWidget(),
            "groupes": Select2MultipleWidget({"data-minimum-input-length": 0}),
        }
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(Formulaire, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'portail_documents_form'
        self.helper.form_method = 'post'
        self.helper.use_custom_control = False

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'

        # Sélectionne uniquement les activités autorisées
        self.fields["type_piece"].queryset = TypePiece.objects.filter(
            Q(structure__in=self.request.user.structures.all()) | Q(structure__isnull=True)
        ).order_by("nom")

        # Activité
        self.fields["activites"].queryset = Activite.objects.filter(
            structure__in=self.request.user.structures.all()
        ).order_by("date_fin")

        # Affichage
        self.helper.layout = Layout(
            utils_commandes.Commandes(annuler_url="{% url 'portail_documents_liste' %}"),
            Fieldset("Généralités",
                Field("titre"),
                Field("texte"),
                Field("couleur_fond"),
            ),
            Fieldset("Document joint",
                Field("document"),
            ),
            Fieldset("Type de pièce associé",
                Field("type_piece"),
            ),
            Fieldset("Public destinataire",
                     Field("activites"),
            ),
            Fieldset("Structure associée",
                Field("structure"),
            ),
        )

EXTRA_HTML = """
<script>
// Sur sélection du public
function On_selection_public() {
    $('#div_id_activites').hide();
    $('#div_id_groupes').hide();
    $('#div_id_periode').hide();
    if ($("#id_public").val() == 'inscrits') {
        $('#div_id_activites').show();
    };
    if ($("#id_public").val() == 'presents') {
        $('#div_id_activites').show();
        $('#div_id_periode').show();
    };
    if ($("#id_public").val() == 'presents_groupes') {
        $('#div_id_groupes').show();
        $('#div_id_periode').show();
    };
}
$(document).ready(function() {
    $('#id_public').on('change', On_selection_public);
    On_selection_public.call($('#id_public').get(0));
});

</script>
"""
