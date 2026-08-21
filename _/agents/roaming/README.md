---
name: mdforge-roaming-guide
memory_type: guide
scope: mdforge
status: active
authority: normative
created: 2026-08-21
last_updated: 2026-08-21
---

# Roaming MDForge — évolution du produit

`roaming/` contient les artefacts en mouvement de MDForge. Il est séparé du code et de la mémoire permanente.

```text
roaming/
├── memory-diagrams/   architecture cible : frontières, responsabilités, expectations
├── targets/           programmes d'implémentation : marches, lots, gates
├── artifacts/         preuves d'exécution agentique et baselines
└── knowledges/        recherches externes de design, non normatives
```

## Démarche canonique

```text
Memory Diagram d'abord
→ Target ensuite
→ marches missionnées
→ preuves
→ intégration
→ promotion des apprentissages durables
```

### Memory Diagram

Décrit ce que MDForge peut/doit devenir. Il distingue explicitement l'observé de la cible et laisse ouvertes les décisions qui ne sont pas mûres.

### Target

Transforme un Memory Diagram en programme d'implémentation exécutable. Une marche n'est cochée qu'après son Gate et ses preuves.

### Artifacts

Prouvent une action ou un état de mission ; ils ne remplacent ni le code ni l'architecture.

### Knowledges

Conservent la matière issue de recherche externe. Un article ou une comparaison n'est jamais une instruction directe : sa substance doit être décidée dans un Memory Diagram.

## Règles

1. lire les deux `00-CANONICAL-READING-ORDER.md` avant de rédiger un diagramme ou un Target ;
2. un document a un seul owner principal et une seule frontière ;
3. référencer plutôt que dupliquer ;
4. chemins complets depuis la racine de `Crackovis/Mdforge` ;
5. code réel au SHA pour toute affirmation d'existence ;
6. pas de cible d'implémentation avant la carte d'architecture correspondante ;
7. PACTE/claims/workspaces restent gouvernés par le host d'exécution, pas par des fichiers locaux simulant une coordination live.
