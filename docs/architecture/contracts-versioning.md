# Versionnement des contrats MDForge T1

Les contrats publics de `mdforge-contracts` suivent SemVer.

- **PATCH** : correction compatible qui ne change pas les entrées/sorties observables.
- **MINOR** : extension rétrocompatible (nouveau champ optionnel, nouveau kind supporté, nouveau DTO).
- **MAJOR** : changement incompatible d'un champ, d'une sémantique de résolution ou d'un protocole.

Une rupture exige une migration explicite, des contract tests mis à jour et une revue d'impact des Targets consommateurs.

Les identités et versions de capabilities utilisent des identifiants stables en minuscules et des versions compatibles PEP 440. Les requirements utilisent des `SpecifierSet` PEP 440. Le format JSON canonique est trié et compact afin de rester déterministe pour les diagnostics, snapshots et futures empreintes.
