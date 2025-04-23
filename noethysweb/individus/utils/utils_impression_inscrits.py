import logging, decimal
logger = logging.getLogger(__name__)
logging.getLogger('PIL').setLevel(logging.WARNING)
from django.db.models import Sum, Q
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib import colors
from core.models import Inscription, Ventilation, Prestation, Rattachement, Cotisation, Tarif, Individu
from core.utils import utils_texte, utils_impression, utils_questionnaires
import os, uuid
from django.conf import settings

class Impression(utils_impression.Impression):
    def __init__(self, *args, **kwds):
        kwds["taille_page"] = landscape(A4) if kwds["dict_donnees"]["orientation"] == "paysage" else portrait(A4)
        super().__init__(*args, **kwds)

    def Draw(self):
        # Importation des inscriptions
        conditions = Q(activite=self.dict_donnees["activite"]) & (Q(date_fin__isnull=True) | Q(date_fin__gte=self.dict_donnees["date_situation"]))
        inscriptions = Inscription.objects.select_related("famille", "individu", "groupe", "categorie_tarif", "activite", "activite__structure").filter(conditions).order_by("individu__nom", "individu__prenom")

        # Calcul des soldes
        dict_ventilations = {temp["prestation_id"]: temp["total"] for temp in Ventilation.objects.values("prestation_id").filter(prestation__activite=self.dict_donnees["activite"]).annotate(total=Sum("montant"))}
        dict_soldes = {}
        for prestation in Prestation.objects.values("famille_id", "individu_id", "pk").filter(activite=self.dict_donnees["activite"]).annotate(total=Sum("montant")):
            key = (prestation["famille_id"], prestation["individu_id"])
            dict_soldes.setdefault(key, decimal.Decimal(0))
            dict_soldes[key] += dict_ventilations.get(prestation["pk"], decimal.Decimal(0)) - prestation["total"]
        del dict_ventilations

        # Recherche des parents
        dict_parents = {}
        liste_enfants = []
        for rattachement in Rattachement.objects.select_related("individu").all():
            if rattachement.categorie == 1:
                dict_parents.setdefault(rattachement.famille_id, []).append(rattachement.individu)
            if rattachement.categorie == 2:
                liste_enfants.append((rattachement.famille_id, rattachement.individu_id))

        def Rechercher_tarifs(inscription=None):
            prestations = Prestation.objects.filter(
                individu=inscription.individu,
                activite=inscription.activite
            ).select_related('tarif')
            return " | ".join(p.label for p in prestations)

        def Rechercher_tel_parents(inscription=None):
            liste_tel = []
            if (inscription.famille_id, inscription.individu_id) in liste_enfants:
                for individu in dict_parents.get(inscription.famille_id, []):
                    if individu.tel_mobile and individu != inscription.individu:
                        liste_tel.append(f"{individu.prenom} : {individu.tel_mobile}")
            return " | ".join(liste_tel)

        def Rechercher_mail_parents(inscription=None):
            liste_mail = []
            if (inscription.famille_id, inscription.individu_id) in liste_enfants:
                for individu in dict_parents.get(inscription.famille_id, []):
                    if individu.mail and individu != inscription.individu:
                        liste_mail.append(f"{individu.prenom} : {individu.mail}")
            return " | ".join(liste_mail)

        # Recherche des cotisations
        dict_cotisations = {}
        for cotisation in Cotisation.objects.filter(date_debut__lte=self.dict_donnees["activite"].date_fin, date_fin__gte=self.dict_donnees["activite"].date_debut).order_by("-date_debut"):
            dict_cotisations.setdefault(cotisation.famille_id, []).append(cotization)

        def Rechercher_cotisation(inscription=None):
            for cotisation in dict_cotisations.get(inscription.famille_id, []):
                if not cotisation.individu_id or cotisation.individu_id == inscription.individu_id:
                    return str(cotisation.numero or "")
            return ""

        # Questionnaires
        questionnaires_individus = utils_questionnaires.ChampsEtReponses(categorie="individu", filtre_reponses=Q(individu__in=[i.individu for i in inscriptions]))
        questionnaires_familles = utils_questionnaires.ChampsEtReponses(categorie="famille", filtre_reponses=Q(famille__in=[i.famille for i in inscriptions]))

        # Préparation des polices
        style_defaut = ParagraphStyle(name="defaut", fontName="Helvetica", fontSize=7, spaceAfter=0, leading=9)
        style_activite = ParagraphStyle(name="centre", fontName="Helvetica-bold", alignment=1, fontSize=8, spaceBefore=0, spaceAfter=20, leading=0)

        # Création du titre du document
        self.Insert_header()

        # Nom de l'activité
        self.story.append(Paragraph(self.dict_donnees["activite"].nom, style_activite))

        # Préparation du tableau
        data_tableau, largeurs_colonnes, ligne = [], [], []

        total_largeurs_fixes = 0
        nbre_colonnes_auto = 0
        for colonne in self.dict_donnees["colonnes_perso"]:
            ligne.append(colonne["nom"])
            total_largeurs_fixes += int(colonne["largeur"]) if colonne["largeur"] != "automatique" else 0
            nbre_colonnes_auto += 1 if colonne["largeur"] == "automatique" else 0
        data_tableau.append(ligne)

        # Calcul des largeurs de colonnes
        largeur_contenu = self.taille_page[0] - 75
        largeur_a_repartir = largeur_contenu - total_largeurs_fixes
        for colonne in self.dict_donnees["colonnes_perso"]:
            if colonne["largeur"] == "automatique":
                largeur = largeur_a_repartir / nbre_colonnes_auto
            else:
                largeur = int(colonne["largeur"])
            largeurs_colonnes.append(largeur)

        # Création des valeurs
        for inscription in inscriptions:
            valeurs = {
                "date_debut": inscription.date_debut.strftime("%d/%m/%Y") if inscription.date_debut else "",
                "date_fin": inscription.date_fin.strftime("%d/%m/%Y") if inscription.date_fin else "",
                "groupe": inscription.groupe.nom,
                "categorie_tarif": inscription.categorie_tarif.nom,
                "tarifs": Rechercher_tarifs(inscription),
                "ind": inscription.individu.get_statut_display(),
                "nom": inscription.individu.nom,
                "prenom": inscription.individu.prenom,
                "date_naiss": inscription.individu.date_naiss.strftime("%d/%m/%Y") if inscription.individu.date_naiss else "",
                "age": str(inscription.individu.Get_age()) if inscription.individu.date_naiss else "",
                "mail": inscription.individu.mail,
                "portable": inscription.individu.tel_mobile,
                "tel_parents": Rechercher_tel_parents(inscription),
                "mail_parents": Rechercher_mail_parents(inscription),
                "individu_ville": inscription.individu.ville_resid,
                "famille": inscription.famille.nom,
                "famille_ville": inscription.famille.ville_resid,
                "num_cotisation": Rechercher_cotisation(inscription),
                "statut": inscription.get_statut_display(),
                "solde": utils_texte.Formate_montant(dict_soldes.get((inscription.famille_id, inscription.individu_id), decimal.Decimal(0))),
            }

            # Ajout des réponses des questionnaires
            valeurs.update({f"question_famille_{question['IDquestion']}": question["reponse"] for question in questionnaires_familles.GetDonnees(inscription.famille_id)})
            valeurs.update({f"question_individu_{question['IDquestion']}": question["reponse"] for question in questionnaires_individus.GetDonnees(inscription.individu_id)})

            # Création de la ligne du tableau
            data_tableau.append([
                Paragraph(str(valeurs.get(colonne["code"], "")), style_defaut)
                for colonne in self.dict_donnees["colonnes_perso"]
            ])

        def smart_key(cell):
            text = cell.text.replace(',', '.').strip()
            try:
                return (0, float(text))  # Priorité aux nombres
            except ValueError:
                return (1, text.lower())  # Ensuite les textes

        data_tableau[1:] = sorted(data_tableau[1:], key=lambda row: smart_key(row[0]))

        # Finalisation du tableau
        style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONT', (0, 0), (-1, -1), "Helvetica", 7),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTRE'),
        ])
        # Création du tableau
        tableau = Table(data_tableau, largeurs_colonnes)
        tableau.setStyle(style)
        self.data_tableau = data_tableau
        self.story.append(tableau)

    def get_csv_response(self):
        from django.http import HttpResponse
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inscriptions.csv"'
        writer = csv.writer(response)

        # Écrire les en-têtes
        headers = [col["nom"] for col in self.dict_donnees["colonnes_perso"]]
        writer.writerow(headers)

        # Écrire les lignes de données
        for row in self.data_tableau[1:]:  # saute la ligne d’en-tête
            writer.writerow([
                cell.text if hasattr(cell, "text") else cell  # .text si c’est un Paragraph, sinon la chaîne
            ])

        return response
