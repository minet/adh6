# Principes

Pourquoi ADH6 est construit comme il l'est. Pour le *comment*, voir [architecture.md](architecture.md) et [developpement.md](developpement.md).

## Motivations

- **Simple à maintenir.** Le code doit rester lisible par quelqu'un qui le découvre. On préfère une solution simple et éprouvée à une solution élégante mais obscure.
- **Backend et frontend séparés.** L'interface peut être refaite sans toucher à la logique métier, et inversement. Ce n'était pas le cas des versions précédentes.
- **Peu de code répétitif.** On s'appuie sur des bibliothèques reconnues et stables (FastAPI, SQLAlchemy, Pydantic, Angular) plutôt que de tout réécrire : moins de lignes, donc moins de bugs.

## Un contrat d'API unique

Le frontend et le backend communiquent en HTTP, selon le contrat décrit dans `openapi/spec.yaml`.

Écrire à la main le client et les modèles des deux côtés serait source d'erreurs : chaque changement d'API devrait être reporté deux fois, et les deux versions finiraient par diverger. On génère donc à partir de la spec :

- les entités Pydantic du backend ;
- le client TypeScript du frontend.

Les routes du backend restent écrites à la main, et un test vérifie qu'elles correspondent toujours à la spec. Le prix à payer est une dépendance à openapi-generator, dont la version est épinglée pour que la génération soit reproductible.

## Clean architecture

Le backend applique une version pragmatique de la [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) de Robert C. Martin : l'application est découpée en couches, chacune avec un rôle précis, et les dépendances pointent toujours vers le métier.

L'objectif est d'avoir une architecture claire sans tomber dans l'excès inverse : on ne passe pas une semaine à concevoir ce qui se code en une heure.

### Les couches

**1. Entités.** Les données manipulées par l'application : un adhérent, une chambre, un appareil. Dans ADH6, elles sont générées depuis la spec (`backend/adh6/entity/`) et partagées par tous les modules.

**2. Cas d'utilisation.** La logique métier (`member_manager.py`, `device_manager.py`…).

Par exemple, valider une cotisation (`SubscriptionManager.validate`) :

> 1. Vérifier que la cotisation attend bien une validation.
> 2. La marquer comme terminée.
> 3. Inscrire l'écriture comptable.
> 4. Prolonger la date de départ de l'adhérent.
> 5. Envoyer le reçu.

Que les données soient dans MySQL ou dans un cahier, que la demande arrive par HTTP ou par un bénévole au comptoir, l'algorithme est le même. C'est cette couche qu'on modifie pour changer le fonctionnement d'ADH.

**3. Adaptateurs.** La couche technique, sans décision métier :

- les **routes** (`router.py`) transforment une requête HTTP en appel au manager, puis traduisent le résultat ou l'erreur en réponse HTTP ;
- les **repositories** (`storage/`) lisent et écrivent en base. Ils se limitent à des opérations simples : toute décision qui ne dépend pas de la technologie de stockage appartient au manager.

### La règle de dépendance

Un manager ne doit importer ni FastAPI, ni SQLAlchemy, ni un repository concret. Il dépend d'**interfaces** (`interfaces/`) : des classes abstraites qui décrivent ce dont il a besoin, par exemple « un `DeviceRepository` sait créer un appareil ». Le repository SQL implémente cette interface, et c'est la route qui assemble les deux.

Sans interface, le manager devrait importer le code de stockage, et la logique métier dépendrait de la technique.