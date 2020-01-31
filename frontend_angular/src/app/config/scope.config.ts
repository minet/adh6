'use strict';

export const SCOPE_LIST = {
  'openid': {
    name: 'openid',
    description: 'Accès élémentaire aux informations suivantes',
    mandatory: true,
    hidden: true
  },
  'profile': {
    name: 'profile',
    description: 'Accès aux informations de base du profil: nom, prénom etc',
    mandatory: true,
    hidden: false
  },
  'offline_access': {
    name: 'offline_access',
    description: 'Autorise l\'application à s\'authentifier automatiquement',
    mandatory: false,
    hidden: false
  },
  'roles': {
    name: 'roles',
    description: 'Accès à la liste des roles pour la gestion des permissions',
    mandatory: false,
    hidden: false
  },
  'account:read': {
    name: 'account:read',
    description: 'Accès à la liste des comptes en trésorerie',
    mandatory: false,
    hidden: false
  }
};
