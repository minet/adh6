# ADH6

## Notes

Je vous invite **vivement** à aller lire [la page sur le wiki](https://wiki.minet.net/wiki/services/adh6) avant de vous plonger dans l'exploration de ce repo.

Si vous voyez une modification à apporter (correction de faute, éclaircissement d'un point, ajout d'instructions supplémentaires, mise à jour d'anciennes informations, etc.) **n'hésitez pas à faire un commit et à vous ajouter dans la liste des contributeurs**. Toute aide est la bienvenue !

## Présentation

ADH est le système de gestion d'adhérents de l'association [MiNET](https://minet.net). Ce document a pour but de présenter la sixième version de notre outil.

## Motivations

Nous voulons produire un outil de gestion des adhérents **simple à maintenir**. Pour cela, nous prônons la _simplicité_ dans _toutes_ les parties de notre projet. Le but est de créer un outil maintenable, qui effectue **sa mission et qui la fait bien**.

Pour cela, nous avons décidé de **dissocier le backend du frontend**. Ainsi, un changement d'interface ne nous obligera pas à réécrire toute la logique du code (comme c'était le cas avec la précédente version).

Pour atteindre ces objectifs, nous essayons de **réduire le code boilerplate** en utilisant des bibliothèques qui sont _réputées et prouvées stables_. Cela permettra d'avoir moins de lignes de code, plus de _lisibilité_ et donc moins de bugs potentiels.

La **fiabilité** de notre outil est aussi un concept important à nos yeux. C'est pour cela que nous faisons beaucoup appel à des **tests d'intégration** (_200+ pour la partie backend pour l'instant_). Nous visons un taux de _code coverage_ le plus haut possible.

## Comment contribuer ?

Allez sur gitlabint.priv.minet.net sur [la page du projet](https://gitlabint.priv.minet.net/services/adh6/adh6/). Si vous n'avez pas les accès, n'hésitez pas à les demander au bureau. Une fois que vous y êtes, allez voir dans les issues, trouvez une qui vous plaît et assignez la vous! N'hésitez pas à demander des précisions sur les issues, on se fera un plaisir de tout vous expliquer et de vous rediriger vers les formation associées!

## OK, maintenant comment je lance en local?

1. Installez _docker_ et _docker-compose_. C'est le système qui va permettre de créer des environnements de dev sur votre machine en local.

2. Modifiez vos DNS locaux pour ajouter `adh6-local.minet.net` vers votre localhost. En général, ajoutez

```
127.0.0.1 adh6-local.minet.net
```

dans votre `/etc/hosts`.

3. Lancez ADH6 en local avec `docker compose up`

Vous devriez pouvoir accéder à https://adh6-local.minet.net/

**NOTE**: Le certificat est auto-signé. Les navigateurs web récents permettent d'activer une option pour toujours faire confiance aux certificats pour localhost.

Chromium: https://stackoverflow.com/questions/7580508/getting-chrome-to-accept-self-signed-localhost-certificate

Avant de continuer, il faut mettre à jour la base de données.
Pour cela, allez dans `api_server/` et faites `./manage.sh seed`.
Cela va appliquer les migrations et mettre des éléments en base.

Pour pouvoir vous connecter, on utilisera directement le CAS de Minet. Il faut vous assurer que `adh6-local.minet.net` est autorisé.

La base de données étant vide, il faudra également vous créer. Vous pouvez utiliser la commande `./manage.sh fake <user>` pour créer un utilisateur admin à votre nom.

Il faut que ce nom soit le même que celui avec lequel vous vous connectez.

Normalement, une fois que le projet est lancé, vous aurez les logs de tous les dockers dans la console.

### Place au dev

Vous avez installé les dépendances etc. dans vos conteneurs, mais pour développer dignement, vous en aurez aussi besoin en local.

Ce projet utilise `uv`. Il vous faudra d'abord l'installer. Ensuite, faites simplement `uv sync`, et vous installerez toutes les dépendances de dev que vous aurez besoin. Pour installer mysqlclient, suiver le guide d'installation de [mysqlclient](https://github.com/PyMySQL/mysqlclient). Votre environnement virtuel est créé sous `.venv/`.

Pour développer et voir vos changements "en direct", vous pouvez utiliser docker compose watch. Dans la console où vous avez effectué `docker compose up`, appuyez sur la touche `w`.  
Maintenant, les changements que vous apportez sont synchronisés avec les conteneurs, et en dev, Angular et Uvicorn vont s'actualiser pour prendre en compte ces changements.

2. Comment ajouter une dépendance Python

`uv add deps`

4. Lancer les tests ?
   Lancez `uv run pytest` dans la console, ou utilisez votre IDE... ce dernier est configuré pour faire en même temps le coverage du code.

Vous pouvez aussi lancer `uv run tox` pour faire à la fois les tests, vérifier le formatage et les types.

#### Frontend

1. Installer les dépendances

```sh
# Sans docker
yarn install --frozen-lockfile
```

2. Ajouter une dépendance : cela dépend du package, il faut voir la librairie directement. Cependant, yarn est le gestionnaire de paquets d'Angular dans ce projet.

# [API](openapi/spec.yaml)

Pour communiquer entre le client et le serveur, nous avons décidé d'utiliser une API.
En termes de techno, on a décidé de prendre la techno la plus stable et universelle (compatible avec tous les futurs projets), HTTP.

Nous avons décidé de ne pas reprogrammer à la main tout un client/serveur pour notre API. Ça aurait été faisable, mais trop sujet à erreurs et on risque de perdre en flexibilité (un changement dans l'API devrait être répercuté dans le code du client ET du serveur). Nous avons donc décidé d'utiliser un système de "génération" de code automatique à partir d'une spec.

Pour définir la spécification de notre API, nous utilisons OpenAPI (anciennement swagger, oui, oui... c'est plus swag).

Pour générer le code serveur, on utilise d'un côté connexion, qui est une librairie Python développée par Zalando. https://github.com/zalando/connexion qui a maintenant été migrée sur ce répo https://github.com/spec-first/connexion. Allez voir le repo, il est assez actif.

Pour le côté client, on utilise directement openapi-generator, (fork de swagger-codegen, édité directement par Swagger). https://github.com/OpenAPITools/openapi-generator Pareil, allez voir leur repo, il est "assez" actif... (12 233 commits à l'heure où j'écris ces lignes, et plus de 1100 contributeurs...)
Ça semble donc aussi être un assez bon choix pour produire un code stable.

En résumé, on a pris le parti pris d'ajouter deux dépendances au projet, mais on a gagné en flexibilité et en maintenabilité.

## Une génération plus simple

Pour plus de flexibilité de génération et assurer une maintenance simple, la génération qui se faisait avec des templates spécifiques à MiNET (après un fork de ceux officiels) est désormais passée sur une génération à partir des templates officiels et d'autres solutions ont été trouvées afin de pallier aux modifications qui avaient été nécessaires.

Ainsi, maintenant pour générer le code ET assurer une consistance dans la génération, il a été décidé d'utiliser docker.

```sh
# dans la racine du projet

# Génération du backend
docker run --rm -u $(id -u):$(id -g) -v ${PWD}:/local openapitools/openapi-generator-cli:latest-release@sha256:c49d9c99124fe2ad94ccef54cc6d3362592e7ca29006a8cf01337ab10d1c01f4 generate -i /local/openapi/spec.yaml -g python-flask -o /local/tmpsrc --additional-properties packageName=adh6 --additional-properties=modelPackage=entity

# Génération du frontend
docker run --rm  -u $(id -u):$(id -g) -v ${PWD}:/local openapitools/openapi-generator-cli:latest-release@sha256:c49d9c99124fe2ad94ccef54cc6d3362592e7ca29006a8cf01337ab10d1c01f4 generate -i /local/openapi/spec.yaml -g typescript-angular -o "/local/frontend_angular/src/app/api" --additional-properties=queryParamObjectFormat=key
```

> Pour assurer la consistance, les hash des images docker ont été utilisés afin d'assurer de toujours avoir le même contexte (notamment les mêmes templates de génération)

### Une consistance dans le code

Pour permettre une meilleure consistance dans le code, nous avons installé [prettier](https://prettier.io/) qui permet de mettre en forme les fichiers JSON, TypeScript, YAML, Angular, entre autres. Pour utiliser prettier, placez-vous dans le dossier frontend.

```sh
cd frontend_angular
```

Pour formater le code, exécutez :

```sh
yarn prettier
```

Pour vérifier si le code est correctement formaté, exécutez :

```sh
yarn prettier:check
```

# [Backend](api_server)

> TODO : renommer le dossier en backend-flask

Si vous voulez directement interagir avec l'API sans vous embêter avec des cURL, allez sur votre navigateur à l'adresse https://ADRESSE-DE-ADH/api/ui

## Je suis perdu, qu'est-ce que c'est que tous ces dossiers ?

Ce projet consiste juste en l'implémentation des différentes méthodes définies dans la spécification de l'API.

Si vous êtes un PGM et que vous voulez juste lire le code, sachez juste que tout le code est dans le dossier [adh6](api_server/adh6).

Pour que Python se comporte en serveur Web, on utilise `Flask`, et pour ne pas avoir à faire de trucs compliqués, on utilise `connexion` qui est la librairie faisant le binding entre Flask et les fonctions en Python qui sont appelées.

Si vous voulez modifier l'API, modifiez le fichier de [spec](openapi/spec.yaml).
Le site permet juste d'avoir une jolie représentation de l'API.

## Architecture

Dans le dossier api_server, le nom des sous-dossiers est assez direct :

- adh6 : contient le code actuel (séparé en modules) assurant le fonctionnement du backend
- test : ensemble des tests du backend
- migration : ensemble des fichiers Python pour assurer la migration du schéma de la DB

### Dossier adh6

La plupart des dossiers sont des modules gérant une partie de la plateforme. Cependant, d'autres servent au fonctionnement global d'ADH6 :

- config : endroit où se trouve la configuration du backend
- default : quelques classes parentes générales servant aux modules (pourraient probablement disparaître).
- storage : gère encore une grande partie du stockage qui sera bientôt gérée directement dans les modules

## Modules

Le serveur peut être séparé en modules. Ces derniers correspondent chacun à une fonctionnalité.

- [**authentication**](api_server/adh6/authentication/README.md) : gère la sécurité des endpoints de la spécification ainsi que des informations concernant l'authentification (clef d'API, rôles utilisateur, ...)
- [**member**](api_server/adh6/member/README.md) : gère les utilisateurs de la plateforme ainsi que l'évolution de leur cotisation.
- [**device**](api_server/adh6/device/README.md) : gère les appareils des membres ainsi que leur attribution d'IP
- [**room**](api_server/adh6/room/README.md) : gère les chambres.
- [**network**](api_server/adh6/network/README.md) : gère les appareils réseaux.
- [**subnet**](api_server/adh6/subnet/README.md) : gère les sous-réseaux à attribuer.
- [**treasury**](api_server/adh6/treasury/README.md) : gère la trésorerie.
- [**metrics**](api_server/adh6/metrics/README.md) : gère les métriques liées à la plateforme.

Un module a de préférence une architecture définie sous la forme suivante.

### Architecture d'un module

Bon.
Au cours de votre vie, vous aurez l'occasion de voir beaucoup de projets faits à l'arrache, sans réelle réflexion sur la façon de construire les choses et qui sont grosso modo dégueulasses et difficilement maintenables.

Vous aurez aussi l'occasion de voir des projets qui sont 'over-designed', où la personne responsable du projet prend 20 ans à réfléchir au bon _design pattern_ à appliquer pour **chaque** fonctionnalité mineure du projet.
Résultat : le projet n'aboutit jamais parce qu'on passe 1 semaine à faire un truc qui se code en 1 heure.

L'objectif, pour ADH, est de vous montrer ce qu'est un projet _backend_ avec une belle architecture, mais sans aller dans l'_over-design_.
J'espère que l'architecture choisie vous convaincra par ses qualités de maintenabilité.
Vous pourrez réutiliser les principes dans d'autres projets (backend ou frontend).

### Clean/Onion architecture

Un type d'architecture qui est grosso modo unanimement reconnu dans le monde de l'info comme un bon modèle est la _clean archi_ telle que décrite par Robert C. Martin (Uncle Bob).

C'est aussi assez connu dans le monde du développement mobile, pour l'anecdote quelqu'un est tombé dessus lors d'un entretien.

[Vous pouvez voir l'article de _Uncle Bob_ sur son blog pour comprendre en détail.](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

![schéma des couches telles que proposées par Uncle Bob](https://blog.cleancoder.com/uncle-bob/images/2012-08-13-the-clean-architecture/CleanArchitecture.jpg)

Le principe est assez classique : vous divisez votre application en couches, qui ont chacune un rôle bien défini.
Le très connu [(si vous avez fait du web) modèle MVC](https://fr.wikipedia.org/wiki/Mod%C3%A8le-vue-contr%C3%B4leur) en est un exemple.

La _clean archi_ en est une généralisation.

Pour comprendre, je vous propose d'analyser ces couches une par une en prenant l'exemple du module [`member`](api_server/adh6/member/).

### Entity layer (Layer 1)

C'est le **coeur** de tous les projets.

Les entités sont en quelque sorte les données gérées par l'application/l'association.

Normalement, un système gère de l'information (sinon ça ne sert à rien de développer une application...), et c'est ça les entités.

Ce sont des structures de données très simples qui ne font que contenir de l'information (ce sont des [DAO](https://en.wikipedia.org/wiki/Data_access_object)s si vous aimez le Java).

Il ne doit pas y avoir de code/logique/algorithme dans cette couche ! C'est juste de la donnée, ce qui donne la raison d'être de l'application.

> **/!\ Pour ADH :** Les _entities_ se trouvent dans le backend global et non dans un module.

ADH est une app de gestion d'adhérents. On retrouve donc une classe `Member`, très simple, qui contient les données utiles à MiNET concernant un adhérent.

On va aussi avoir d'autres données que l'application va gérer comme les chambres (`room`) ou le réseau (`port`, `switch` et `vlan`).

### Use case (Layer 2)

C'est le comportement de l'application.

Il contient ce qu'on appelle la _Business logic_:
Quand vous avez un cas d'utilisation et que vous l'exprimez sous la forme d'un algorithme, c'est ce que vous allez mettre dans cette couche.

Cet algorithme doit être **TOTALEMENT** indépendant de la partie technique. Autrement dit, que ce soit une API HTTP qui communique avec du SQL, ou alors une personne réelle qui prend en charge les adhérents en notant les adhésions sur un carnet, l'algorithme doit être **le même**.

Vous allez toucher à cette couche quand vous voudrez changer le fonctionnement de ADH.

**Pour ADH :** pour la cotisation d'un adhérent
Si on avait à écrire en pseudocode ça donnerait un truc du genre :

> 1. Quand tu reçois une demande d'adhésion (que ce soit un gars qui te demande ou un appel HTTP)
> 2. Inscris une nouvelle écriture comptable dans le livre journal (on ne sait pas si c'est un livre journal physique ou une base de données)
> 3. Enregistre que l'adhérent a cotisé jusqu'au 12 janvier 2100... (pareil, peu importe où on enregistre, ce n'est pas notre problème dans cette couche)
> 4. Active le port de l'adhérent (on pourrait utiliser une communication directe avec un switch ou alors demander à un admin de SSH sur le switch et de le faire manuellement)

Bon, dans ADH, plutôt qu'en pseudo-code on l'a fait en Python... Mais c'est presque pareil ! :D

Cette façon de faire, sans jamais mentionner la technique, nous permet de nous abstraire de TOUTE dépendance à une bibliothèque ou technologie qu'on utilise.

Si jamais un jour on ne veut plus utiliser MySQL, mais Redis ou Elasticsearch pour stocker des données... Eh bien on n'aura pas à modifier ces deux premières couches.
Pareil, si on en a marre des API REST et qu'on veut utiliser gRPC ou autre, on pourra.

Encore plus important : si on utilise une bibliothèque/framework comme Flask, connexion et SQLAlchemy et que l'un vient à être abandonné (ou qu'il y a une grosse faille de sécu), l'application n'en dépend pas et on n'aura pas à TOUT modifier.

**Point important : Vous ne devez pas importer des bibliothèques ni des classes de la prochaine couche ici. (Voir la _law of include_ de l'article d'Uncle Bob)**

> Point important, dans ADH, on appelle ces fichiers des **manager**. On aura donc dans le module `member` le `member_manager.py`, ... Ces derniers se trouvent à la racine du module.

### Interface handler (Layer 3)

C'est la couche technique.
Très clairement, vous ne définissez aucun comportement de l'application ici, vous faites juste une interface entre le monde et l'application.

Si jamais vous changez la technologie derrière ADH, vous irez faire des modifs ici.

**Pour ADH:**

_Pour le stockage_, vous allez faire des classes qui implémentent les opérations de base [CRUD (Create, Read, Update, Delete)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) et jamais plus compliqué. Toutes les opérations plus compliquées, ou les décisions qui n'ont pas de rapport avec la technologie utilisée derrière doivent être mises dans les use cases.
Ça doit rester simple !

_Pour l'API_ : les points d'entrée de l'application se trouvent aussi dans cette couche.
Puisqu'on arrive dans l'appli par un appel HTTP, on a des fonctions qui vont gérer la requête, transformer les données brutes en entité, faire appel aux use cases, et renvoyer les bons codes d'erreur HTTP.

### Framework & drivers (Layer 4)

Cette partie, ça ne correspond pas vraiment à notre code mais plutôt aux dépendances qu'on utilise.
Ici on va retrouver SQLAlchemy, connexion, Flask, le client Elasticsearch, etc...

En gros, c'est le contenu de requirements.txt.

## Un exemple de bout en bout...

Je vais prendre un exemple simple: la création d'un appareil.

Vous (en tant qu'utilisateur) faites une requête HTTP vers adh6.minet.net contenant la MAC de votre nouvel appareil.

1. Les bibliothèques _connexion_ et _Flask_ utilisées par ADH6 prennent cette requête, et l'interprètent. (Layer 4)
   Les bibliothèques appellent une fonction Python.

2. Une fonction Python (dans le [device http handler](api_server/adh6/device/http/device.py)) reçoit la requête HTTP et la transforme en une entité, un truc compréhensible pour l'application sans avoir aucun lien avec la techno utilisée pour recevoir le message. (Layer 3) Cette fonction va ensuite appeler la méthode `create(self, ctx, body: DeviceBody) -> Device` du [device manager](api_server/adh6/device/device_manager.py).

3. Le [device manager](api_server/adh6/device/device_manager.py) va lire l'entité de l'appareil, vérifier que l'adresse MAC est bien valide, que tout est bon (layer 2), et va faire une demande à un [device repository](api_server/adh6/device/interfaces/device_repository.py) (interface abstraite qui représente un moyen de stocker des appareils, voir les notes ci-dessous en italique), de sauvegarder l'appareil.

4. [`DeviceSQLRepository`](api_server/adh6/device/storage/device_repository.py) est une classe qui implémente (en gros elle satisfait toutes les contraintes) [DeviceRepository](api_server/adh6/device/interfaces/device_repository.py), elle est utilisée par le device manager et va utiliser SQLAlchemy pour créer (bêtement) un appareil. (Layer 3)

5. SQLAlchemy contacte le serveur MySQL (MariaDB) pour faire l'écriture (Layer 4)

_Une interface est une sorte de patron, un moule, une contrainte, par exemple... un repository pour appareil doit au moins avoir une méthode qui permet de créer un appareil... Ces interfaces font partie de la couche 2_

_Si vous vous posez des questions sur pourquoi je vous parle des interfaces, allez lire l'article d'Uncle Bob sur la Law of Include, en théorie on n'a pas le droit (dans le use case) d'importer des fichiers de interface_handler.
Utiliser une interface permet de dépasser cette limitation_

Comme vous pouvez le voir, lors de chaque appel, on rentre dans l'_onion_ de la couche 4 à 1 (même s'il n'y a pas de code, la couche 1 est utilisée grâce aux entities).
Puis on ressort de la couche 1 à 4 pour interagir avec le monde à nouveau.

Ce cas d'utilisation est assez simple. Finalement, il ne fait que valider la MAC de l'appareil, mais certains cas sont plus complexes, comme celui pour faire cotiser un adhérent.
Dans ce cas il faut valider les données, écrire dans le livre comptable, ajouter une adhésion, changer la date de départ du membre, et _log_ l'action (parce que la traçabilité c'est important).
Il faut aussi gérer les cas d'erreur.

# [Frontend](frontend_angular)

_NOTE : nous utilisons la version 14 d'Angular_

![diagramme des vues](flux_adh6.png)

Voici le diagramme de toutes les vues d'ADH6 pour son cas d'utilisation
principal (c'est-à-dire, gérer les profils d'adhérents).

### Mettre à jour l'API dans Angular

Contrairement au backend, lorsque vous faites une modification dans spec.yaml, cette modification n'est pas reportée dans le code du frontend.
Il faut manuellement re-générer le code pour communiquer avec l'API pour le mettre à jour.

Pour cela, `make generate` et c'est fini !

## CAS

### Description

CAS est le service qui gère l'authentification des actions des utilisateurs.

Le protocole utilisé est OAuth2.

## Questions?

Si vous avez des interrogations en lisant ce README sur la clean archi, c'est normal. Allez lire l'article d'Uncle Bob et cherchez un peu sur internet, voire regardez les formations actuelles qui ont été faites par _frazew_ et _vaktas_.
Une fois que vous avez trouvé la solution, ajoutez ci-dessous votre question/réponse.

Sinon vous pouvez contacter Vaktas directement (n'oubliez pas que vous pouvez utiliser cette archi dans vos autres projets).

### Pourquoi se faire chier à faire 3 couches alors qu'on pourrait tout mettre dans les fonctions dans interface_handler/http_api ?

> Comme dit précédemment, parce que le jour où tu voudras changer de techno tu seras tellement dépendant de tes libs que tu devras tout refaire.
>
> Un autre critère important est la testabilité. En découpant en couches, tu peux faire des tests unitaires pour tes use cases très facilement en 'mockant' ta couche des interface handlers.
>
> Tu peux faire des tests d'intégration pour tester... l'intégration avec ton SQL/server web. etc.
>
> Enfin, l'argument principal est l'inversion de dépendance (le D des principes SOLID https://en.wikipedia.org/wiki/SOLID)
>
> (et puis c'est plus facile de bosser avec des projets qui ont une archi claire et unifiée!)

### Tu nous parles d'indépendance des technos... Mais on est toujours dépendant de Python...

> Oui. On peut difficilement faire plus indépendant que le langage de prog choisi. (Voir les raisons de pourquoi Python sur le wiki)

Cependant, avec le changement d'architecture qui a été fait avec le passage d'une _clean architecture_ globale au projet à une _clean architecture_ locale aux modules, on pourrait se retrouver avec une API interne passant par les jetstreams NATS (techno à la mode pour les dialogues entre les Micro Services)

# Cas d'utilisation

On peut identifier les fonctions principales d'ADH - celles qui doivent toujours marcher et qui doivent bien être testées.

### Core use cases

La première priorité est que l'on puisse enregistrer des cotisations pendant la permanence, et ça nous permet de dégager une première liste des _use cases_ prioritaires (_core use cases_).
Ces cas d'utilisation sont ceux qui seront **toujours** utilisés lors d'une permanence (où il y a du monde).

En gros, si une de ces fonctionnalités est _down_, on ne peut pas faire la perm' et la personne qui doit réparer a bien la pression. :D

- Ajouter une adhésion (`MemberManager.new_membership`): Pour faire cotiser les membres de l'association.
- Ajouter un membre (`MemberManager.update_or_create`): Pour les nouveaux adhérents, il faut pouvoir leur créer un profil.
- Lire le profil d'un membre (`MemberManager.get_by_username`): Pour accéder au profil d'un adhérent et vérifier que sa cotisation a bien été faite
- Ajouter un appareil (`DeviceManager.update_or_create`): Pour ajouter un nouvel appareil au compte de l'adhérent pour qu'il puisse se connecter au réseau.
- Chercher des appareils (`DeviceManager.search`): Pour chercher les appareils d'un adhérent (nécessaire pour voir tous les appareils sur son profil).

### Level 2 use cases

Ces cas d'utilisation sont des fonctionnalités dont on a très souvent besoin en permanence mais qui ne sont pas indispensables.

Si une de ces fonctionnalités est _down_ on peut encore inscrire les gens et leur fournir un accès internet.
Certaines personnes devront repasser plus tard pour qu'on leur règle leur problème mais ça doit être une minorité.

En gros pendant la perm' tout le monde va râler, mais on peut encore fonctionner en mode dégradé.

- Lire les logs de quelqu'un (`MemberManager.get_logs`): Pour aider à débugger les problèmes des adhérents.
- Supprimer un appareil (`DeviceManager.delete`): Pour virer une MAC d'un profil adhérent
- Changer le mot de passe d'un membre (`MemberManager.change_password`): Pour changer le mot de passe d'un membre.
- Mettre à jour le profil d'un membre (`MemberManager.update_partially`): Pour changer les infos d'un membre ou le faire déménager de chambre.
- Chercher les membres (`MemberManager.search`): Pour ne pas à avoir à taper exactement le _username_ des adhérents et pouvoir chercher leur profil avec leur nom.
- Voir les infos d'un appareil (`DeviceManager.get_by_mac_address`): Pour voir les infos d'un appareil (par exemple ses IPs)
- Supprimer un appareil (`DeviceManager.delete`): Pour virer une MAC d'un profil adhérent

### Level 3 use cases

C'est principalement des cas utilisés lors de la gestion en dehors des perms.
Si ces fonctionnalités tombent en panne ça n'affectera pas du tout (ou très peu) les perms.
Dans le pire des cas on peut se permettre d'aller dans la base de données pour faire manuellement les actions.

Ces cas d'utilisation sont ajoutés à ADH pour notre propre confort mais ne sont pas indispensables.

- Supprimer un membre (`MemberManager.delete`) : Supprimer un adhérent de notre base de données, par exemple dans le cadre du droit à l'effacement de la RGPD (article 17).
