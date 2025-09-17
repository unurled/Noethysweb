import logging
from outils.views.procedures import BaseProcedure
from core.models import Structure, Activite

logger = logging.getLogger(__name__)

class Procedure(BaseProcedure):
    def Arguments(self, parser=None):
        """
        Cette procédure ne prend pas d'argument.
        Elle parcourt toutes les structures de la base.
        """
        pass

    def Executer(self, variables=None):
        try:
            # Parcours toutes les structures
            structures = Structure.objects.all()
            total_modifiees = 0

            for structure in structures:
                if not structure.visible:
                    # Met toutes les activités liées à cette structure en invisible
                    modifiees = Activite.objects.filter(structure=structure).update(visible=False)
                    total_modifiees += modifiees

            return f"Nombre total d'activités rendues invisibles : {total_modifiees}"

        except Exception as e:
            logger.error(f"Une erreur est survenue : {str(e)}")
            return f"Une erreur est survenue : {str(e)}"
