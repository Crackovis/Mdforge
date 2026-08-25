# Handoff T1 — Fondation microkernel et capability runtime

## Statut

T1 établit le socle constitutionnel de MDForge : contrats versionnés, découverte par entry points, registry, résolution déterministe, contexte borné, lifecycle transactionnel, bundles génériques et Application Runtime API commune aux surfaces humaines et machine.

Baseline de mission :

- `Crackovis/Mdforge@master` : `4aa40da65b22d2f0fe4de2b4638cfc41e704aa15` ;
- MDDOCX : `92095562b1d9b421c3c5cc7f761c16b74115c5a7` ;
- Python d'acceptance : `3.14.7` avec contrat `>=3.12` ;
- uv : `0.12.5`.

## Frontières gelées pour T2

T2 peut consommer sans connaître les internals du kernel :

- `CapabilityIdentity` ;
- `CapabilityManifest` ;
- `ServiceContract` et `Requirement` ;
- `CapabilityProvider` ;
- `RuntimeContext` ;
- `RuntimeEvent` ;
- `StructuredError` ;
- sémantique du `CapabilityRegistry` ;
- résolution de dépendances et sélection explicite de provider ;
- `RuntimeBundle` ;
- `MdforgeApplication` comme façade applicative unique.

Toute rupture future de ces frontières exige version de contrat, migration, contract tests et impact review T2/T3.

## Preuves rejouables

### Batterie finale

Preuves durables BOSSMCP finales :

- `TASK-FA0230ADAEB5` (`mdforge-t1-final-quality-v6`) : qualité complète ;
- `TASK-CB326366F4F4` (`mdforge-t1-final-fresh-runtime-v6`) : build, fresh install et runtime installé ;
- `TASK-843AFF7A0E30` (`mdforge-t1-final-plugin-constitution-v6`) : package tiers install/run/remove et invariance kernel.

Résultats :

- `uv sync --locked --all-packages` : PASS ;
- pytest complet : `40 passed in 0.56s` ;
- Ruff : `All checks passed!` ;
- mypy strict : `Success: no issues found in 11 source files` ;
- build des cinq packages : PASS ;
- cinq wheels principaux : `py3-none-any` ;
- fresh install à partir des wheels uniquement : PASS dans un venv Python 3.14.7 recréé de zéro ;
- `mdforge doctor --json` : READY, trois capabilities, zéro échec de discovery ;
- pipeline événementiel installé : `discovered → validated → resolved → starting → started → ready` ;
- discovery embarquée distincte des entry points : PASS ;
- machine d'état capability `resolved → prepared → active → stopping → stopped/failed` : PASS ;
- `mdforge capabilities` humain et `--json` : même vérité applicative ;
- scénario d'activation défaillante : `failed-clean`, rollback complet, aucune capability active ;
- package tiers installable/exécutable/retirable sans patch kernel : PASS.

### Runtime frais

Le fresh install a produit :

```json
{"capability_count":3,"discovery_failures":[],"ready":true,"runtime":"mdforge-t1"}
```

Le bundle `reference.echo + reference.consumer` a démontré :

```text
reference.echo start
→ reference.consumer start
→ consume reference.echo = "echo:hello"
→ runtime.ready
→ consumer stop
→ echo stop
→ active_capabilities = []
```

Le scénario `reference.echo + reference.failing` a démontré :

```text
reference.echo start
→ reference.failing start échoue
→ reference.echo stop pendant rollback
→ runtime = failed-clean
→ erreur primaire conservée
→ rollback_errors = []
→ active_capabilities = []
```

### Test constitutionnel plugin tiers

Un package séparé `mdforge-external-sample` a été :

```text
build
→ install dans le fresh venv
→ discovery via mdforge.capabilities
→ activation de external.sample
→ stop propre
→ uninstall
→ disparition du registry
```

Digest des sources kernel avant installation et après retrait :

```text
087d06ec1700843ed4ac8b46948da4ac6801b306c17ca2b44219de2da6a4349c
```

Le kernel n'a donc pas été patché pour ajouter ou retirer la capability tierce.

### Fitness functions constitutionnelles

Les tests actifs vérifient explicitement :

- manifest incomplet refusé ;
- IDs, versions et requirements invalides refusés ;
- bundle référençant une capability absente refusé ;
- sélection explicite de provider invalide refusée ;
- optional requirements tolérés ;
- missing/incompatible/ambiguous providers diagnostiqués ;
- cycles diagnostiqués ;
- ordre topologique stable ;
- service non déclaré inaccessible ;
- start/stop idempotents dans les états terminaux ;
- rollback propre et rollback partiellement défaillant classifiés distinctement ;
- package `contracts` indépendant du kernel ;
- kernel indépendant de l'application, de la CLI et des plugins ;
- plugin de référence indépendant des internals du kernel ;
- absence de dépendances runtime plateforme ou prématurées dans T1.

### MDDOCX

`git submodule status Mddocx` conserve :

```text
92095562b1d9b421c3c5cc7f761c16b74115c5a7
```

`git diff --submodule=short -- Mddocx` est vide.

## Décision Pluggy

Pluggy n'est pas retenu dans le kernel T1.

Le spike architectural conclut qu'il n'existe pas encore de problème de hooks 1→N nécessitant une abstraction supplémentaire. `importlib.metadata` couvre la découverte ; `CapabilityRegistry`, le resolver et le lifecycle possèdent des responsabilités explicites qui ne doivent pas être capturées par un framework de hooks. Une fitness function vérifie que `packages/kernel` ne dépend pas directement de `pluggy`.

Cette décision peut être réouverte si une target future démontre un vrai besoin de hooks multiples indépendants ; elle ne doit pas être anticipée.

## Politique de timeout T1

Aucun mécanisme de timeout n'est introduit dans le kernel T1. Le runtime natif livré ici n'exécute ni subprocess, ni service distant, ni MCP, ni I/O bloquante sous contrôle du kernel : ajouter un timeout générique à ce stade créerait une infrastructure sans besoin démontré. Les runtimes externes prévus par les targets ultérieures devront définir leur politique de timeout lorsqu'ils introduiront effectivement des opérations bloquantes ou distantes, avec tests et rollback adaptés.

## Portabilité et écarts de preuve

Linux headless est exécuté réellement. Les wheels sont `py3-none-any` et une fitness function interdit dans le corpus T1 les imports de runtime spécifiques/différés (`win32com`, `pythoncom`, `comtypes`, `subprocess`, `socket`, `sqlite3`, `fastapi`, `mcp`). T1 ne dépend ni de Word/COM, ni d'un daemon, ni d'une base distante.

Le worker BOSSMCP courant ne fournit pas d'hôte Windows : aucun run Windows natif n'est déclaré. L'écart est explicite et borné ; la portabilité Windows de T1 repose à ce stade sur le caractère Python pur des distributions et l'absence de dépendance plateforme, conformément à la clause du Target autorisant un écart explicitement prouvé.

## Particularité d'environnement observée

Le worker BOSSMCP injecte un `PYTHONPATH` de son runtime Python 3.10 dans les sous-processus. Un premier smoke frais a donc tenté de charger le Pydantic du BOSSMCP. Le fresh-install gate canonique neutralise `PYTHONPATH`, `PYTHONHOME`, `VIRTUAL_ENV` et `PYTHONUSERBASE`, puis fixe `PYTHONNOUSERSITE=1`. Avec cet environnement propre, le runtime installé depuis wheels est vert.

Ce point est une caractéristique de l'environnement d'exécution BOSSMCP, pas une dépendance de MDForge.

## Handoff T2

T2 peut maintenant implémenter Project Discovery comme capabilities séparées produisant Project/Source/Document Graph, sans introduire de logique documentaire dans le kernel. Les prochaines capabilities doivent être distribuables par entry point et consommer uniquement les contrats publics T1.
