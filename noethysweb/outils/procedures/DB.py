import logging
logger = logging.getLogger(__name__)
from outils.views.procedures import BaseProcedure
from django.conf import settings


class Procedure(BaseProcedure):
    def Executer(self, variables=None):
        # Récupérer le chemin du fichier SQLite depuis la configuration
        db_path = settings.DATABASES["default"]["NAME"]

        # Retourner simplement le chemin du fichier
        return db_path
