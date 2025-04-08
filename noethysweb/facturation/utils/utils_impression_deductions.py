# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import logging, decimal
from reportlab.platypus import Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from core.models import Prestation, Activite, Deduction
from core.utils import utils_impression, utils_texte

logger = logging.getLogger(__name__)
logging.getLogger("PIL").setLevel(logging.WARNING)


class Impression(utils_impression.Impression):
    def Draw(self):
        # Importation des prestations
        if self.dict_donnees["activites"]["type"] == "groupes_activites":
            liste_activites = [a.pk for a in Activite.objects.filter(groupes_activites__in=self.dict_donnees["activites"]["ids"])]
        else:
            liste_activites = self.dict_donnees["activites"]["ids"]

        prestations = Prestation.objects.select_related("famille", "activite", "individu", "facture").filter(
            activite_id__in=liste_activites,
            date__range=self.dict_donnees["periode"]
        ).order_by("individu__prenom")

        deductions = Deduction.objects.select_related("label", "famille", "prestation").filter(prestation__in=prestations)

        dict_deductions_famille = {}
        recapitulatif = {}

        for deduction in deductions:
            prestation = deduction.prestation
            key = (deduction.famille, prestation.label, deduction.label)
            dict_deductions_famille.setdefault(key, decimal.Decimal(0))
            dict_deductions_famille[key] += deduction.montant

            # Récapitulatif
            recap_key = (deduction.label,)
            if recap_key not in recapitulatif:
                recapitulatif[recap_key] = {
                    "montant": decimal.Decimal(0),
                    "familles": set(),
                    "prestations": set()
                }
            recapitulatif[recap_key]["montant"] += deduction.montant
            recapitulatif[recap_key]["familles"].add(deduction.famille)
            recapitulatif[recap_key]["prestations"].add(prestation.label)

        # Styles
        style_defaut = ParagraphStyle(name="defaut", fontName="Helvetica", fontSize=7, spaceAfter=0, leading=9)
        style_centre = ParagraphStyle(name="centre", fontName="Helvetica", alignment=1, fontSize=7, spaceAfter=0, leading=9)

        # Titre
        self.Insert_header()
        self.story.append(Paragraph("<b>Période du %s au %s</b>" % (
            self.dict_donnees["periode"][0].strftime("%d/%m/%Y"),
            self.dict_donnees["periode"][1].strftime("%d/%m/%Y")
        ), style_centre))
        self.story.append(Spacer(0, 15))

        # === TABLEAU DETAIL ===
        dataTableau = [("Famille", "Prestation", "Déduction", "Montant")]

        for (famille, prestation_label, deduction_label), montant in sorted(dict_deductions_famille.items(), key=lambda x: (x[0][0].nom, x[0][1], str(x[0][2]))):
            dataTableau.append((
                Paragraph(famille.nom, style_defaut),
                Paragraph(prestation_label, style_defaut),
                Paragraph(str(deduction_label), style_defaut),
                Paragraph(utils_texte.Formate_montant(montant), style_centre),
            ))

        tableau = Table(dataTableau, [140, 120, 120, 50])
        tableau.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
        ]))
        self.story.append(tableau)
        self.story.append(Spacer(0, 15))

        # === TABLEAU RECAPITULATIF ===
        dataRecap = [("Déduction", "Nbre familles", "Nbre prestations", "Montant total")]

        for (deduction_label,), infos in sorted(recapitulatif.items(), key=lambda x: str(x[0])):
            dataRecap.append((
                Paragraph(str(deduction_label), style_defaut),
                Paragraph(str(len(infos["familles"])), style_centre),
                Paragraph(str(len(infos["prestations"])), style_centre),
                Paragraph(utils_texte.Formate_montant(infos["montant"]), style_centre),
            ))

        total_montant = sum(i["montant"] for i in recapitulatif.values())
        dataRecap.append((
            Paragraph("<b>Total</b>", style_defaut),
            "", "", Paragraph("<b>%s</b>" % utils_texte.Formate_montant(total_montant), style_centre),
        ))

        tableau_recap = Table(dataRecap, [180, 80, 100, 80])
        tableau_recap.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONT", (0, 0), (-1, -1), "Helvetica", 7),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
        ]))
        self.story.append(tableau_recap)
