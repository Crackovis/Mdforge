# AGENTS.md — MDForge

> **Repository** : `Crackovis/Mdforge`
> **Contexte canonique** : `infrastructure:mdforge`
> **Finalité** : construire une forge documentaire Markdown modulaire par principe, robuste, agent-native et pratique, sans laisser les contraintes historiques de MDDOCX définir l'architecture future.

## 1. Identité du projet

MDForge est l'owner de l'infrastructure documentaire `infrastructure:mdforge`.

Le dépôt contient aujourd'hui une coquille minimale et le submodule `Mddocx/`. Cette réalité observée ne doit pas être confondue avec l'architecture cible : MDForge est appelé à devenir une forge documentaire composable dont MDDOCX constitue une capacité historique et un premier moteur de production, pas le noyau conceptuel entier.

## 2. Ordre de démarrage

Un agent qui travaille dans ce repository lit, dans cet ordre :

1. `AGENTS.md` ;
2. `manifest.yaml` ;
3. `_/agents/INDEX.md` ;
4. `_/agents/roaming/README.md` ;
5. `_/agents/roaming/memory-diagrams/00-CANONICAL-READING-ORDER.md` ;
6. les Memory Diagrams actifs de la frontière concernée ;
7. `_/agents/roaming/targets/00-CANONICAL-READING-ORDER.md` puis le Target actif si la mission implémente une cible ;
8. le code réel au SHA chargé et les contrats/tests nécessaires seulement.

Quand MDForge est monté dans TAKOUDJOU Research Center, la gouvernance globale de `Crackovis/Researches` et PACTE-BOSS restent supérieures pour la coordination, les claims, les worktrees, Git et les preuves. Le présent réseau possède uniquement la connaissance et l'évolution **spécifiques à MDForge**.

## 3. Plans étanches

```text
_/agents/                 → control plane MDForge : orientation et mémoire locale
_/agents/roaming/         → évolution du produit : Memory Diagrams, Targets, preuves, knowledges
code/runtime              → vérité de ce qui existe réellement
Mddocx/                   → submodule propriétaire, frontière Git indépendante
```

Ne pas copier dans MDForge la mémoire institutionnelle de Researches. Ne pas déposer la doctrine produit MDForge dans MDDOCX.

## 4. Démarche d'évolution

```text
Memory Diagram
→ Target
→ marches missionnées
→ tests / preuves
→ intégration
→ apprentissages promus
```

Le Memory Diagram cartographie ce que MDForge **doit pouvoir devenir**. Le Target décide comment l'implémenter. Un fichier, une classe ou un commit ne constitue jamais à lui seul une preuve de comportement.

## 5. Principes non négociables actuels

1. **Modularité par principe** : les capacités variables vivent hors du kernel minimal et se composent par contrat.
2. **Markdown natif** : Markdown est le substrat d'auteur principal ; sa représentation physique ne doit pas dicter le modèle documentaire interne.
3. **MDDOCX ≠ MDForge** : MDDOCX est une capacité/moteur historique à préserver et à intégrer proprement, pas le modèle d'architecture global.
4. **Profil de publication ≠ format de sortie** : une thèse, un article ou un rapport ne sont pas des renderers DOCX/PDF/HTML.
5. **Human-native et agent-native** : CLI, UI, API et MCP doivent converger vers les mêmes cas d'usage applicatifs.
6. **Reproductibilité** : toute forge sérieuse doit pouvoir expliquer ses inputs, sa composition, ses versions, ses diagnostics et ses artefacts.
7. **Safe by default** : génération candidate/snapshot avant écrasement d'un artefact autoritaire.
8. **Contrats avant plugins** : extensibilité sans frontières testables n'est qu'un monolithe distribué.

## 6. Git et submodule

- `Crackovis/Mdforge` possède la logique MDForge et le pointeur vers MDDOCX.
- `Crackovis/Mddocx` possède son code ; toute mutation MDDOCX se fait dans ce repository puis le pointeur MDForge est re-pointé séparément si la mission l'exige.
- Pas de `--force`.
- Pour une mission complexe : mission + claim + workspace isolé + preuves + handoff.
- Une branche de travail ne devient pas vérité de `master` avant intégration prouvée.

## 7. Autorité

```text
comportement observé au SHA chargé
> code et contrats actifs
> Memory Diagram actif pour l'architecture cible
> Target actif pour le programme d'implémentation
> handoff / état de mission
> archives historiques
```

Pour une question d'architecture future, le Memory Diagram gouverne. Pour une affirmation « cela existe », le code et la preuve au SHA gouvernent.
