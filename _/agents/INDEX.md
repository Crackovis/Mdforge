---
node_id: mdforge-agent-index
memory_type: index
scope: mdforge
status: active
authority: canonical
created: 2026-08-21
last_updated: 2026-08-21
repositories:
  - Crackovis/Mdforge
---

# Index canonique du réseau d'agents MDForge

Porte d'entrée locale pour `infrastructure:mdforge`.

## Chargement minimal

```text
AGENTS.md
→ manifest.yaml
→ _/agents/INDEX.md
→ _/agents/roaming/README.md
→ contrat Memory Diagrams
→ Memory Diagram actif pertinent
→ contrat Targets + Target actif si implémentation
→ code / tests au SHA réel
```

## Carte

```text
_/agents/
├── INDEX.md
├── memory/
│   └── README.md
├── skills/
│   └── README.md
└── roaming/
    ├── README.md
    ├── memory-diagrams/
    │   ├── 00-CANONICAL-READING-ORDER.md
    │   └── 01-product-architecture/
    ├── targets/
    │   └── 00-CANONICAL-READING-ORDER.md
    ├── artifacts/
    │   └── README.md
    └── knowledges/
        └── README.md
```

## Nœud actif de fondation

- `_/agents/roaming/memory-diagrams/01-product-architecture/memory-diagram-mdforge-modular-agent-native-document-forge.md`

Ce diagramme est une **architecture cible**, pas une affirmation sur l'état du code.

## Frontières de connaissance

- Le réseau local porte la mémoire de **produit et d'architecture MDForge**.
- La gouvernance Researches/PACTE reste chez `Crackovis/Researches` lorsque ce dépôt est monté dans TAKOUDJOU.
- La mémoire propre à MDDOCX reste chez l'owner MDDOCX ; MDForge ne la copie pas.
- Les recherches externes de design vont dans `roaming/knowledges/`, puis leur substance doit être promue dans un Memory Diagram avant d'influencer un Target.

## Autorité

1. comportement observé et tests au SHA réel ;
2. code/contrats actifs ;
3. Memory Diagrams actifs pour l'architecture cible ;
4. Targets actifs pour l'exécution ;
5. handoffs et preuves de mission ;
6. archives.
