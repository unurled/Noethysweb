# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.db.models import Q
from core.models import Individu, Rattachement


def Get_renseignements_manquants(famille=None):
    """
    Retourne le nombre de renseignements manquants pour une famille et l'ID du premier rattachement concerné.
    Vérifie les champs obligatoires pour chaque membre de la famille.
    Retourne un dictionnaire: {'nbre': nombre, 'premier_rattachement_id': id ou None, 'page_cible': 'identite' ou 'coords'}
    """
    if not famille:
        return {'nbre': 0, 'premier_rattachement_id': None, 'page_cible': None}
    
    nbre_manquants = 0
    premier_rattachement_id = None
    page_cible = None
    
    # Récupération de tous les individus rattachés à la famille
    rattachements = Rattachement.objects.select_related('individu').filter(famille=famille, individu__deces=False)
    
    for rattachement in rattachements:
        individu = rattachement.individu
        individu_manquants = 0
        manquant_identite = False
        manquant_coords = False
        
        print("Vérification de l'individu:", individu)
        
        if not individu.nom:
            individu_manquants += 1
            manquant_identite = True
        if not individu.prenom:
            individu_manquants += 1
            manquant_identite = True
        
        # Champs obligatoires pour tous (identité)
        if not individu.civilite:
            individu_manquants += 1
            manquant_identite = True
        if not individu.date_naiss:
            individu_manquants += 1
            manquant_identite = True
        if not individu.cp_naiss:
            individu_manquants += 1
            manquant_identite = True
        if not individu.ville_naiss:
            individu_manquants += 1
            manquant_identite = True
            
        # Vérification des coordonnées pour les parents (titulaires et représentants)
        print("rattachement", rattachement)
        print("rattachement.titulaire", rattachement.titulaire)
        print("rattachement.categorie", rattachement.categorie)
        if rattachement.categorie == 1:  # Représentant
            if not individu.rue_resid:
                individu_manquants += 1
                manquant_coords = True
            if not individu.cp_resid:
                individu_manquants += 1
                manquant_coords = True
            if not individu.ville_resid:
                individu_manquants += 1
                manquant_coords = True
            if not individu.tel_mobile and not individu.tel_domicile:
                print('manquant tel sans parent')
                individu_manquants += 1
                manquant_coords = True
            if not individu.mail:
                print('manquant mail sans parent')
                individu_manquants += 1
                manquant_coords = True
        else:
            # Pour les enfants, vérifier si au moins un parent a des coordonnées complètes
            parents = Rattachement.objects.filter(
                famille=famille,
                individu__deces=False
            ).filter(Q(titulaire=True) | Q(categorie=1))
            
            has_parent_with_coords = False
            for parent_ratt in parents:
                parent = parent_ratt.individu
                if (parent.rue_resid and parent.cp_resid and parent.ville_resid and 
                    (parent.tel_mobile or parent.tel_domicile) and parent.mail):
                    has_parent_with_coords = True
                    break
            
            # Si aucun parent n'a de coordonnées complètes et que l'enfant n'en a pas non plus
            if not has_parent_with_coords:
                if not individu.rue_resid:
                    print('manquant rue_resid')
                    individu_manquants += 1
                    manquant_coords = True
                if not individu.cp_resid:
                    print('manquant cp_resid')
                    individu_manquants += 1
                    manquant_coords = True
                if not individu.ville_resid:
                    print('manquant ville_resid')
                    individu_manquants += 1
                    manquant_coords = True
        
        # Mémoriser le premier rattachement avec des manquants
        if individu_manquants > 0:
            if premier_rattachement_id is None:
                premier_rattachement_id = rattachement.pk
                # Prioriser l'identité si des champs y sont manquants, sinon coordonnées
                if manquant_identite:
                    page_cible = 'identite'
                elif manquant_coords:
                    page_cible = 'coords'
            nbre_manquants += individu_manquants
    
    return {'nbre': nbre_manquants, 'premier_rattachement_id': premier_rattachement_id, 'page_cible': page_cible}
