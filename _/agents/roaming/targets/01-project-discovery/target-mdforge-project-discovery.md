---
name: target-mdforge-project-discovery
memory_type: target
scope: mdforge
status: draft
authority: target
profile: A
created: 2026-08-24
last_updated: 2026-08-24
source_context:
  - memory-diagrams/01-product-architecture/memory-diagram-mdforge-modular-agent-native-document-forge.md
baseline:
  mdforge: a9023cc5efc96314d6590ed17e5fabe3bb6fdd61   # coquille minimale (documenté 2026-08-21)
  mddocx: 92095562b1d9b421c3c5cc7f761c16b74115c5a7   # submodule (documenté 2026-08-21)
  note: "L'agent vérifie les SHAs courants au SHA chargé au démarrage de la mission."
related_targets:
  - target-mdforge-kernel-contracts            # à naître — kernel minimal (famille 1)
  - target-mdforge-plugin-runtime              # à naître — registry/manifests (famille 3)
  - target-mdforge-build-engine                # à naître — plan/exécution/preuve (famille 4)
---

# Target — Project Discovery : Source Pattern & Document Graph

> **Promesse** : un utilisateur — humain ou agent — peut décrire **comment son
> répertoire Markdown se lit** (chapitres = répertoires, sections = sous-répertoires
> ou fichiers, sous-sections = titres dans les fichiers), enregistrer ce schéma de
> lecture, et MDForge **scanne le répertoire racine selon ce schéma** pour produire
> un graphe documentaire inspectable — avant toute compilation.

## 1. Contexte — cas d'usage opérateur (verbatim condensé)

> « MDForge veut que les utilisateurs se lèvent un bon matin et ils ont un projet sur
> lequel ils veulent travailler. Ils utilisent leur Text Editor afin de travailler sur
> des fichiers Markdown. Ils arrangent leur répertoire et ils définissent une espèce
> de pattern de lecture de leur répertoire : "dans mon environnement de travail, les
> chapitres représentent tel répertoire nommé de telle façon ; les fichiers Markdown
> qui s'y trouvent ne font que représenter les sections au sein d'un chapitre ; et à
> l'intérieur de chaque fichier Markdown, il y a les sous-sections si le rédacteur le
> veut bien." Ou bien il pourrait vouloir faire autrement : le répertoire représente
> un chapitre, les sous-répertoires représentent une section, les sous-sous-répertoires
> une autre section. Ils définissent cette façon dynamique, ils enregistrent le schéma,
> et MDForge procède au scan du répertoire racine. »

La thèse du Memory Diagram §5 : **MDForge n'est pas un convertisseur Markdown→X,
c'est un moteur de composition de capacités documentaires dont Markdown est le
substrat d'auteur natif.** Ce target pose la première frontière stable de cette
forge : **la découverte** — passer d'un répertoire physique à une structure logique
sans figer la stratégie de scan dans le kernel (Memory Diagram §6 : « stratégie de
scan d'un projet imposée à tous » = ce que le kernel ne doit PAS posséder).

Les conventions de compilation actuelles restent d'actualité et définissent les
comportements historiques à préserver : `Mddocx/MDDOCX_CONVENTIONS.md` (nommage
`NN_MM_nom.md`, fichiers `_xxx` ignorés, parents triés avant sous-sections, formats
de légendes/formules) et `Mddocx/README.md` (pipeline sources → preflight → build,
kinds de ressources). Le pattern de lecture déclaratif de ce target **formalise**
ces conventions plutôt qu'il ne les remplace.

## 2. Promesse de la cible

Après ce target, MDForge sait, pour un projet donné :

1. **lire le pattern de lecture déclaratif** de l'utilisateur (schéma enregistré) ;
2. **scanner le répertoire racine** conformément à ce pattern ;
3. **produire un Document Graph minimal** : unités documentaires (chapitres →
   sections → sous-sections), ordre logique, chemins sources, fichiers ignorés,
   ambiguïtés et diagnostics du scan ;
4. **exposer ce graphe** à un humain (CLI) et à un agent (mêmes données structurées).

Sans : compiler, styler, référencer, résoudre des assets, choisir une topologie.

## 3. Périmètre

### Inclus

- Contrat de la **capability `source-pattern`** : schéma déclaratif (format
  libre JSON/YAML à décider — pas de topologie imposée), règles de validation,
  enregistrement/lecture d'un pattern par projet.
- **Scanner** : parcours du répertoire racine selon le pattern (répertoires =
  chapitres, sous-répertoires = sections, fichiers = sections/sous-sections,
  titres Markdown = sous-sections ; variantes dynamiques combinables).
- **Document Graph minimal** : modèle de données des unités documentaires et de
  leurs relations, indépendant des noms de dossiers (invariant §6.6 du Memory
  Diagram).
- **Surface d'inspection** : commande/API « comprendre ce projet » (lister la
  structure, les fichiers ignorés, les diagnostics) — humaine et agent-native.
- Tests rejouables + fixtures représentatives.

### Exclu (frontières explicites)

- Refonte de l'architecture existante de MDDOCX (aucun big-bang).
- Renderers (DOCX/PDF/HTML/EPUB/LaTeX) — targets ultérieurs.
- Résolution de références, assets, styles, profils de publication.
- Build Plan / Build Run / Build Record — target `build-engine`.
- Plugin runtime (registry, manifests, isolation) — target `plugin-runtime`.
- Choix backend/frontend/data/MCP (Memory Diagram §10 : ouvert).
- GUI.

## 4. Exigences fonctionnelles

- **EF1 — Pattern déclaratif** : l'utilisateur décrit son arborescence dans un
  fichier de pattern (ex. `mdforge.pattern.*` à la racine du projet) : règle
  « chapitre = répertoire », « section = sous-répertoire » ou « section = fichier »,
  « sous-section = titre Markdown `##` », conventions de nommage (préfixes
  numériques), fichiers/répertoires ignorés (convention `_` existante), tri.
- **EF2 — Variantes combinables** : un même pattern accepte des arborescences
  différentes (2 ou 3 niveaux de répertoires, sections dans les fichiers…),
  validées par le schéma — le rédacteur choisit SA façon, pas une imposée.
- **EF3 — Scan déterministe** : même racine + même pattern = même graphe (ordre
  stable, indépendant du système de fichiers).
- **EF4 — Diagnostics structurés** : fichier orphelin, section sans parent,
  doublon de numérotation, fichier non-Markdown, ambiguïté — listés, pas
  silencieux.
- **EF5 — Inspection** : `mdforge inspect <projet>` (ou équivalent API) affiche
  la structure logique complète : chapitres, sections, sous-sections, chemins
  sources, ordre, ignorés, diagnostics.
- **EF6 — Agent-native** : mêmes données en sortie structurée (JSON) pour un
  agent, sans parser une UI ni un traceback.

## 5. Exigences architecturales (héritées du Memory Diagram)

- La stratégie de scan vit **dans la capability**, pas dans le kernel (MD §6).
- **Contract-first** : le pattern et le graphe ont des contrats versionnés et
  testables (MD §7.2, §14.4).
- **Graph-aware** : la structure logique est un modèle explicite, pas la liste de
  fichiers (MD §7.4).
- **Project-aware** : le pattern appartient au projet (MD §7.3).
- **Inspectable** : le scan s'inspecte avant tout build (MD §7.8).
- **Portable** : le cœur ne dépend pas de Windows/Word (MD §7.13).
- **Headless-first** : CLI/API d'abord ; pas de dépendance GUI (MD §7.11).
- Le kernel reste petit : toute logique spécifique de scan est une capability
  remplaçable (MD §14.1-14.2).

## 6. Marches

### Marche 1 — Contrat `source-pattern`

- **Promesse** : le schéma déclaratif du pattern de lecture existe, est versionné,
  validable, et s'enregistre/lit par projet.
- **Lots**
  - [ ] Contrat du pattern : structure minimale (règles de mapping
        répertoire/fichier/titre, nommage, ignorés, tri), exemple canonique.
  - [ ] Validateur : un pattern invalide produit des erreurs bornées.
  - [ ] Fixture : au moins 2 patterns représentatifs (arborescence 2 niveaux +
        sections dans fichiers ; arborescence 3 niveaux).
  - [ ] `owned_paths` : `src/mdforge/capabilities/source_pattern/` + `contracts/`
        + `tests/fixtures/patterns/`.
- **Gate** : fixture validée par le validateur ; erreurs attendues reproduites.

### Marche 2 — Scanner & Document Graph minimal

- **Promesse** : `scan(racine, pattern)` produit un graphe documentaire
  déterministe + diagnostics.
- **Lots**
  - [ ] Modèle Document Graph minimal (unités : chapitre/section/sous-section ;
        ordre ; chemins ; statut ignoré).
  - [ ] Scanner conforme au pattern (2 niveaux et 3 niveaux, sections en fichiers).
  - [ ] Diagnostics structurés (orphelins, doublons, non-markdown, `_` ignorés).
  - [ ] Fixture réelle : un mini-projet de type « thèse » (miroir de la convention
        `NN_MM_nom.md` de v0.3) dans `tests/fixtures/projects/`.
  - [ ] `owned_paths` : `src/mdforge/capabilities/discovery/` +
        `src/mdforge/model/document_graph/`.
- **Gate** : le scan de la fixture « thèse » produit le graphe attendu (comparaison
  déterministe) et les diagnostics exacts listés.

### Marche 3 — Surface d'inspection (CLI + sortie structurée)

- **Promesse** : un humain et un agent « comprennent » un projet avec la même
  commande.
- **Lots**
  - [ ] `mdforge inspect <projet>` : sortie lisible (arborescence logique,
        ordre, ignorés, diagnostics).
  - [ ] Sortie structurée JSON identique (flag `--json` ou équivalent).
  - [ ] Test de parcours agent : inspecter → lire le graphe → localiser une
        section précise → rapporter les diagnostics (sans UI).
  - [ ] `owned_paths` : `src/mdforge/cli/` (ou adaptateur de surface désigné).
- **Gate** : le parcours agent de bout en bout passe sur la fixture « thèse » ;
  humain et agent obtiennent les mêmes données.

## 7. Preuves exigées (au Gate de chaque marche)

- Tests rejouables (pytest ou équivalent) dans `tests/`, fixtures dans
  `tests/fixtures/`.
- Sortie du scan déterministe : graphe + diagnostics, versionnés en fixture
  attendue (golden files).
- Démonstration du cas d'usage opérateur : un répertoire type « thèse » est
  compris par MDForge (chapitres → sections → sous-sections) sans configuration
  autre que le pattern enregistré.
- Aucune mutation de MDDOCX (submodule intact).

## 8. Définition de terminé

- [ ] EF1-EF6 démontrées par tests et par le parcours agent.
- [ ] Le kernel ne contient aucune stratégie de scan codée en dur (la logique
      vit dans la capability).
- [ ] MDDOCX n'a pas été modifié ; son corridor Word reste fonctionnel.
- [ ] Handoff rédigé : état, preuves, chemins possédés, frontières ouvertes
      (plugin-runtime, build-engine).

## 9. Contraintes & gouvernance

- Aucun `--force` ; mission + claim + workspace isolé avant mutation.
- `owned_paths` distincts par lot pour permettre la parallélisation.
- Rollback défini avant mutation (le pattern et le graphe ne touchent rien de
  MDDOCX).
- Toute évolution de contrat partagé précède ses consommateurs.
- L'agent en ligne démarre par l'ordre de lecture canonique du repo MDForge
  (AGENTS.md → manifest.yaml → _/agents/INDEX.md → roaming/README →
  00-CANONICAL-READING-ORDER → memory diagram → ce target → code au SHA chargé).

## 10. Frontières partagées (handshakes à venir)

| Target futur | Frontière partagée |
|---|---|
| `kernel-contracts` | notions d'unité documentaire, de capability et de contrat versionné |
| `plugin-runtime` | enregistrement de la capability `source-pattern` / `discovery` |
| `build-engine` | le Document Graph comme entrée du Build Plan |
| `publication-profiles` | le pattern de lecture comme input des profils (ex. thèse WUST) |
