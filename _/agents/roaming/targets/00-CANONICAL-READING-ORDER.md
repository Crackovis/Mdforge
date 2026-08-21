---
name: mdforge-targets-canonical-reading-order
memory_type: governance
scope: mdforge
status: active
authority: canonical
created: 2026-08-21
last_updated: 2026-08-21
applies_to:
  - _/agents/roaming/targets/**/*.md
---

# Contrat de rédaction — Targets MDForge

Un Target est un **programme d'implémentation exécutable dérivé d'un Memory Diagram**. Il ne redéfinit pas l'architecture et ne prouve rien par sa seule existence.

## Règles minimales

1. `source_context` référence le ou les Memory Diagrams actifs ;
2. `baseline` porte les SHAs exacts des repositories impliqués ;
3. chaque marche a une **Promesse**, des **Lots** et un **Gate** vérifiable ;
4. une marche est suivie par `- [ ]` / `- [x]` et n'est cochée qu'après le Gate ;
5. les frontières partagées sont explicites (`related_targets`, handshakes) ;
6. les lots parallèles possèdent des `owned_paths` distincts ;
7. tout changement de contrat partagé précède la parallélisation de ses consommateurs ;
8. rollback, tests, preuves et handoff sont définis avant mutation ;
9. les Targets clos vont dans `00-archives/` ; un Memory Diagram source reste actif tant qu'un document actif en dépend.

## Profil A

Cible bornée : une ou quelques marches directes, pas d'orchestration artificielle.

## Profil B

Cible multi-frontières : marches numérotées, lots parallélisables, lot d'intégration par marche, handshakes, stop conditions et définition de terminé.

## Nommage

```text
targets/NN-<axe>/target-mdforge-<slug>.md
```

## Vérité de progression

```text
checkbox du Target + Gate + preuve
= progression réelle
```

Un commit, un fichier présent ou une déclaration d'agent n'est jamais une clôture suffisante sans la preuve exigée par le Gate.
