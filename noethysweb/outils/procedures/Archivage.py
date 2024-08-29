import logging
logger = logging.getLogger(__name__)
from outils.views.procedures import BaseProcedure
from core.models import Article, Activite, Structure, PortailDocument

class Procedure(BaseProcedure):
    def Arguments(self, parser=None):
        # Aucune modification nécessaire ici pour le moment
        pass

    def Executer(self, variables=None):
        try:
            # Vérification que l'activité a été fournie
            activites = variables.get('activite')
            if not activites:
                return "Aucune activité sélectionnée."

            # Récupérer tous les articles liés aux activités sélectionnées
            articles_modifies = Article.objects.filter(
                activites__in=activites
            ).update(structure=12, statut='non_publie')
            strucdocument_modifies = PortailDocument.objects.filter(
                activites__in=activites
            ).update(structure=12)
            actdocument_modifies = PortailDocument.objects.filter(
                structure=12
            )
            # Ajoute l'activité 23 aux documents trouvés
            for doc in actdocument_modifies:
                doc.activites.set([23])
            return f"Nombre d'articles modifiés : {articles_modifies}, Nombre de documents modifiés : {strucdocument_modifies}"

        except Exception as e:
            logger.error(f"Une erreur est survenue : {str(e)}")
            return f"Une erreur est survenue : {str(e)}"
