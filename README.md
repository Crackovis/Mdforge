# MDForge

MDForge est l'infrastructure documentaire `infrastructure:mdforge` : une forge Markdown appelée à devenir modulaire par principe, composable, reproductible et utilisable aussi naturellement par un humain que par un agent.

## État observé

Au baseline de fondation (`a9023cc5efc96314d6590ed17e5fabe3bb6fdd61`), le repository reste une coquille légère :

- `Mddocx/` est le submodule `Crackovis/Mddocx` ;
- `launch_mdforge.bat` délègue encore au lanceur MDDOCX ;
- la logique MDForge unifiée n'est pas encore implémentée.

Cet état ne doit pas être confondu avec l'architecture cible.

## Direction architecturale

La réflexion de refondation est portée par :

`_/agents/roaming/memory-diagrams/01-product-architecture/memory-diagram-mdforge-modular-agent-native-document-forge.md`

Principe central : **MDForge est un moteur de composition de capacités documentaires ; MDDOCX est une capacité/moteur historique spécialisé, pas le kernel entier.**

## Pour les agents

Commencer par `AGENTS.md`, puis `_/agents/INDEX.md`.

Le pipeline d'évolution est :

```text
Memory Diagram → Target → marches → preuves → intégration
```

## Usage historique actuel

```bat
launch_mdforge.bat
```

Ce launcher conserve le corridor existant vers MDDOCX tant que la nouvelle architecture n'a pas été implémentée et prouvée.
