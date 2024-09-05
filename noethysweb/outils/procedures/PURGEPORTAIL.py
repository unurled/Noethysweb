#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import logging
logger = logging.getLogger(__name__)
from outils.views.procedures import BaseProcedure
from core.models import PortailRenseignement  # Assurez-vous que le modèle est importé correctement

class Procedure(BaseProcedure):
    """
    Procédure pour mettre à jour les renseignements en attente en 'VALIDE' si validation_auto est True.
    Pour exécuter : utilisez la commande correspondante sans argument.
    """
    def Arguments(self, parser=None):
        # Pas de paramètres nécessaires pour cette procédure
        pass

    def Executer(self, variables=None):
        # Récupérer tous les renseignements en attente
        renseignements = PortailRenseignement.objects.filter(etat="ATTENTE", validation_auto=True)

        # Mettre à jour l'état de chaque renseignement
        nb_mis_a_jour = 0
        for renseignement in renseignements:
            renseignement.etat = "VALIDE"
            renseignement.save()
            nb_mis_a_jour += 1

        # Log et retourner le nombre d'éléments mis à jour
        logger.info(f"{nb_mis_a_jour} renseignements mis à jour en 'VALIDE'.")
        return f"{nb_mis_a_jour} renseignements ont été mis à jour en 'VALIDE'."