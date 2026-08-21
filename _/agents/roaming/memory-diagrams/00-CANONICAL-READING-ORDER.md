---
node_id: mdforge-memory-diagrams-canonical-reading-order
memory_type: governance
scope: mdforge
status: active
authority: canonical
created: 2026-08-21
last_updated: 2026-08-21
applies_to:
  - _/agents/roaming/memory-diagrams/**/*.md
---

# Contrat de rédaction — Memory Diagrams MDForge

## 1. Nature

Un Memory Diagram est une **carte d'architecture canonique ou cible**. Il précède l'implémentation et nourrit les Targets.

```text
Memory Diagram → ce qui peut/doit exister
Target         → comment l'implémenter et le prouver
Preuve         → ce qui existe réellement au SHA observé
```

Toujours distinguer :

```text
vérité observée au SHA
≠ architecture cible
≠ état committé
≠ preuve runtime
```

## 2. Deux profils

### Profil A — simple

Une frontière unique, un sujet borné, peu de dépendances.

Minimum : frontmatter, portée/vérité, frontières, responsabilités, références.

### Profil B — orchestré

Plusieurs frontières, fondation de plusieurs Targets, implications transversales ou doctrine produit.

Minimum :

1. portée et niveau de vérité ;
2. sources de vérité / ordre de lecture ;
3. préséance ;
4. vocabulaire égalisé ;
5. architecture de responsabilité ;
6. implications/invariants ;
7. dépendances et Targets aval ;
8. questions ouvertes ;
9. cycle de vie ;
10. contrôle avant mission.

Le diagramme fondateur MDForge relève du profil B.

## 3. Frontmatter

Un diagramme déclare au minimum :

```yaml
node_id: stable-id
memory_type: architecture_target | architecture_canonical
scope: mdforge
status: active | archived
authority: target | canonical
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
review_after: YYYY-MM-DD
primary_context_ref: infrastructure:mdforge
repositories: []
root_references: []
research_inputs: []
supersedes: null
```

Une affirmation `observed` doit porter un SHA exact dans le corps ou le frontmatter.

## 4. Rangement et nommage

```text
memory-diagrams/
├── 00-CANONICAL-READING-ORDER.md
├── 00-archives/
└── NN-<axe>/
    └── memory-diagram-mdforge-<slug>.md
```

Un document transversal est référencé, jamais dupliqué. Les préfixes numériques règlent la navigation, pas l'autorité.

## 5. Bonnes pratiques

- séparer clairement **faits**, **expectations**, **invariants** et **questions ouvertes** ;
- dessiner les responsabilités avant de nommer les classes ou frameworks ;
- préférer les concepts stables aux détails d'implémentation prématurés ;
- exprimer ce que le système **ne possède pas** ;
- rendre visibles les axes encore à explorer plutôt que simuler une décision ;
- toute inspiration externe reste un `research_input`, jamais une autorité ;
- faire émerger les futurs Targets depuis des frontières architecturales, pas depuis une liste de fichiers à modifier.

## 6. Préséance

Pour l'architecture cible : diagramme spécialisé > Target > artefact de mission.

Pour l'existence réelle : preuve reproductible > code au SHA > récit documentaire.

Une cible livrée peut faire évoluer le diagramme ; elle ne le réécrit pas implicitement.

## 7. Cycle de vie

```text
création
→ Targets dérivés
→ évolutions versionnées / supersedes
→ architecture stabilisée
→ éventuellement promotion vers mémoire durable
→ archivage seulement si aucun actif n'en dépend
```

Un diagramme peut survivre à tous les Targets qui l'ont réalisé.
