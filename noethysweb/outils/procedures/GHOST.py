import logging
from outils.views.procedures import BaseProcedure
from core.models import Famille, Historique, Prestation

logger = logging.getLogger(__name__)

class Procedure(BaseProcedure):
    def Arguments(self, parser=None):
        """
        Supprime les familles qui ne se sont jamais connectées au portail et
        qui n'ont jamais eu d'inscription.
        """
        pass

    def Executer(self, variables=None):
        total_supprimees = 0
        erreurs = []

        # IDs des familles ayant au moins une connexion
        familles_connectees_ids = Historique.objects.filter(
            titre="Connexion au portail"
        ).values_list('famille_id', flat=True).distinct()

        # IDs des familles ayant au moins une inscription
        familles_inscrites_ids = Prestation.objects.values_list('famille_id', flat=True).distinct()

        # Familles à supprimer : ni connectées, ni inscrites
        familles_a_supprimer = Famille.objects.exclude(
            idfamille__in=familles_connectees_ids
        ).exclude(
            idfamille__in=familles_inscrites_ids
        )

        for famille in familles_a_supprimer:
            try:
                famille.delete()
                total_supprimees += 1
            except Exception as e:
                erreurs.append(f"Erreur pour la famille {famille.idfamille} : {str(e)}")
                logger.error(f"Erreur pour la famille {famille.idfamille} : {str(e)}")

        resultat = f"Nombre de familles supprimées : {total_supprimees}"
        if erreurs:
            resultat += "\nErreurs rencontrées :\n" + "\n".join(erreurs)

        return resultat
