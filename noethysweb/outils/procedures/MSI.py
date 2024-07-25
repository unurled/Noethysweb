#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

import logging
logger = logging.getLogger(__name__)
from outils.views.procedures import BaseProcedure
from core.models import Individu, Rattachement


class Procedure(BaseProcedure):
    def Arguments(self, parser=None):
        # Si vous avez besoin de paramètres spécifiques, vous pouvez les ajouter ici
        pass

    def Executer(self, variables=None):
        try:
            # Mettre à jour les individus
            individus_modifies = Individu.objects.filter(
                rattachement__categorie=2
            ).update(statut=5)

            return f"Nombre d'individus modifiés : {individus_modifies}"

        except Exception as e:
            return f"Une erreur est survenue : {str(e)}"

