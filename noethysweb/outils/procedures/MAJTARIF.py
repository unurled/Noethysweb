import logging
from outils.views.procedures import BaseProcedure
from core.models import Tarif, Prestation, TarifLigne

logger = logging.getLogger(__name__)

class Procedure(BaseProcedure):
    def Arguments(self, parser=None):
        pass

    def Executer(self, variables=None):
        try:
            tarif = variables.get('tarif')
            if not tarif:
                return "Aucun tarif sélectionné."

            # Récupère la ligne de tarif unique associée
            tarif_ligne = TarifLigne.objects.filter(tarif=tarif).first()
            if not tarif_ligne:
                return "Aucune ligne de tarif trouvée pour ce tarif."

            nouveau_montant = tarif_ligne.montant_unique

            # Mise à jour des prestations liées
            prestations_modifiees = Prestation.objects.filter(tarif_id=tarif).update(
                montant=nouveau_montant,
                montant_initial=nouveau_montant
            )

            return f"Nombre de prestations modifiées : {prestations_modifiees}"

        except Exception as e:
            logger.error(f"Une erreur est survenue : {str(e)}")
            return f"Une erreur est survenue : {str(e)}"
