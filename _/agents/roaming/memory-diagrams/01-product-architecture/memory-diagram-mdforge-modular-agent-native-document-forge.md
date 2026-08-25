---
node_id: memory-diagram-mdforge-modular-agent-native-document-forge
memory_type: architecture_target
scope: mdforge
status: active
authority: target
created: 2026-08-21
last_updated: 2026-08-25
review_after: 2026-09-25
primary_context_ref: infrastructure:mdforge
linked_context_refs:
  - publication:wust-master-thesis-v03
repositories:
  - Crackovis/Mdforge
  - Crackovis/Mddocx
root_references:
  - AGENTS.md
  - manifest.yaml
  - _/agents/INDEX.md
  - _/agents/roaming/README.md
  - _/agents/roaming/memory-diagrams/00-CANONICAL-READING-ORDER.md
research_inputs:
  - https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
  - https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
  - https://docs.astral.sh/uv/concepts/projects/workspaces/
  - https://pluggy.readthedocs.io/
  - https://github.com/modelcontextprotocol/python-sdk
  - https://typer.tiangolo.com/
  - https://rich.readthedocs.io/
  - https://www.sqlite.org/
supersedes: null
---

# Memory Diagram — MDForge, forge documentaire modulaire et agent-native

## 1. Portée et niveau de vérité

Ce document fixe **l'architecture cible de réflexion et de conception** de MDForge avant la rédaction de ses Targets d'implémentation.

Il ne prétend pas que cette architecture est déjà implémentée.

### Vérité observée au baseline

Au SHA MDForge `a9023cc5efc96314d6590ed17e5fabe3bb6fdd61` :

- le repository est une coquille MDForge minimale ;
- `launch_mdforge.bat` délègue encore au sous-projet MDDOCX ;
- `Mddocx/` est un submodule au SHA `92095562b1d9b421c3c5cc7f761c16b74115c5a7` ;
- le manifest identifie déjà le produit comme `infrastructure:mdforge`.

Tout le reste de ce document est **architecture_target** : expectations, frontières, baseline technologique candidate et hypothèses de conception à transformer plus tard en Targets et preuves.

```text
OBSERVÉ
MDForge shell → MDDOCX

CIBLE
MDForge = forge composable autonome
MDDOCX = source historique d'exigences et de comportements
         → migration vers des capabilities MDForge
         → retrait après parité prouvée
```

## 2. Sources de vérité et ordre de lecture

```text
AGENTS.md
→ manifest.yaml
→ _/agents/INDEX.md
→ contrat Memory Diagrams
→ CE diagramme
→ futur(s) Target(s)
→ code / tests au SHA de mission
```

Quand le repository est monté dans TAKOUDJOU, les contrats institutionnels de Researches gouvernent la coordination et PACTE ; MDForge ne les recopie pas.

## 3. Préséance

```text
Architecture future
  ce Memory Diagram
  > Targets dérivés
  > artefacts de mission

Existence réelle
  preuve reproductible
  > code/contrats au SHA chargé
  > documentation
```

Une API, une stack ou une capability imaginée ici n'existe pas tant qu'un Target ne l'a pas livrée et prouvée.

## 4. Vocabulaire égalisé

| Terme | Sens architectural |
|---|---|
| **Forge** | système qui transforme un projet documentaire en artefacts traçables selon une composition de capacités |
| **Microkernel** | noyau minimal qui connaît contrats, découverte, contexte de services, cycle de vie, composition, exécution et preuve — pas les domaines documentaires particuliers |
| **Capability / Plugin** | unité remplaçable ou composable apportant une capacité ; elle peut être native, exécutable, service, MCP ou adapter de plateforme |
| **Capability Contract** | identité et contrat déclaratif d'une capability : ce qu'elle fournit, requiert, supporte et peut affecter |
| **Capability Registry** | registre résolu des capabilities disponibles et de leurs contrats |
| **Service Context** | graphe runtime des services/capabilities montés et de leurs dépendances |
| **Profile / Bundle** | composition nommée et versionnée de capabilities et de configuration |
| **Project** | contexte d'une production : sources, configuration, profils, assets, références, politiques et outputs attendus |
| **Document Graph** | représentation structurée du contenu et de ses relations, indépendante du simple layout de fichiers |
| **Publication Profile** | conventions d'un produit documentaire : thèse, article, rapport, livre, etc. |
| **Renderer / Output Capability** | capacité qui matérialise un artefact : DOCX, PDF, HTML, EPUB, LaTeX, etc. |
| **Pipeline / Recipe** | composition explicite de capacités pour un build donné |
| **Build Plan** | plan résolu avant effets : capacités, ordre, inputs, outputs, diagnostics attendus |
| **Build Run** | exécution réelle d'un Build Plan |
| **Build Record** | trace reproductible du build réellement exécuté |
| **Artifact** | sortie produite : document, rapport, manifeste, preview, logs structurés, etc. |
| **Application API** | surface applicative unique consommée par CLI, UI, SDK, automatisations et MCP |
| **Agent Surface** | interface structurée permettant à un agent d'inspecter, planifier, compiler et diagnostiquer |

Les technologies nommées plus bas sont des **candidates à prototyper** sauf lorsqu'elles sont explicitement marquées comme invariants constitutionnels.

## 5. Théorème de conception

> **MDForge n'est pas un convertisseur Markdown→X. C'est un runtime de composition documentaire modulaire, local-first et agent-native, dont Markdown est le substrat d'auteur natif.**

La modularité n'est pas un choix de rangement du code. Elle est le mécanisme même par lequel le produit existe.

```mermaid
flowchart TD
    I["Intention<br/>Human / CLI / UI / Agent / MCP"]
    APP["Application API"]
    K["MDForge Microkernel"]

    R["Capability Registry"]
    C["Service Context / Dependency Graph"]
    L["Lifecycle + reversible effects"]
    P["Profiles / Bundles / Composition"]
    X["Execution + Build Ledger"]

    I --> APP --> K
    K --> R
    K --> C
    K --> L
    K --> P
    K --> X

    R --> G["Capability Graph"]
    C --> G
    P --> G

    G --> BP["Build Planner"]
    BP --> DG["Document Graph"]
    DG --> B["Build Plan"]
    B --> X
    X --> A["Artifacts + Build Record + Evidence"]
```

### 5.1 Constitution minimale du microkernel

Le kernel ne doit posséder **aucune connaissance directe** de :

```text
Markdown
DOCX / Word
PDF / HTML / LaTeX
WUST / IEEE / conventions de thèse
Pandoc / Mermaid / LaTeX engines
bibliographie particulière
GUI / TUI
MCP
```

Il possède uniquement les primitives nécessaires pour :

1. découvrir et identifier les capabilities ;
2. valider leurs contrats ;
3. résoudre leurs dépendances/services ;
4. monter et démonter leurs effets de façon réversible ;
5. composer des profiles/bundles ;
6. préparer une exécution déterministe ;
7. exécuter et produire un Build Record vérifiable.

Le **Build Planner** est une pièce motrice importante, mais il ne doit pas devenir un nouveau monolithe. Le kernel lui fournit le contexte et les contrats ; sa stratégie doit rester testable et remplaçable derrière une interface stable.

### 5.2 Principe constitutionnel — everything variable is a capability

Une fonctionnalité ne devient pas « core » parce qu'elle est importante.

Elle devient core uniquement si **aucun MDForge cohérent ne peut exister sans elle**.

```mermaid
flowchart LR
    K["Microkernel"]

    K --> S["Source / Discovery"]
    K --> PA["Parser"]
    K --> ST["Structure"]
    K --> RE["References"]
    K --> AS["Assets"]
    K --> TR["Transform"]
    K --> PR["Publication Profile"]
    K --> OU["Output"]
    K --> VA["Validation"]
    K --> EX["External Tool"]
    K --> US["Usage Surface"]
```

Ce principe s'inspire de l'idée « everything is a plugin » de DeepSeek Harness/Cordis, mais MDForge l'adapte au domaine documentaire et à ses contraintes de reproductibilité, de fichiers, d'outils externes et de publication.

### 5.3 Un plugin n'est pas nécessairement du Python

C'est une condition essentielle pour que MDForge puisse bénéficier de logiciels existants au lieu de les réécrire.

```mermaid
flowchart TD
    CC["Capability Contract"]

    CC --> N["Native capability<br/>Python in-process"]
    CC --> E["Executable capability<br/>process / stdio"]
    CC --> S["Service capability<br/>local or remote API"]
    CC --> M["MCP capability<br/>MCP client/server"]
    CC --> O["Platform capability<br/>Word COM / OS adapter"]

    N --> CTX["MDForge Context"]
    E --> CTX
    S --> CTX
    M --> CTX
    O --> CTX
```

Conséquences :

- Pandoc peut être une executable capability ;
- Mermaid CLI peut être une executable capability ;
- Microsoft Word COM reste une platform capability Windows ;
- un moteur distant peut être une service capability ;
- un logiciel déjà MCP-native peut être raccordé par un MCP capability adapter ;
- un plugin léger de confiance peut vivre in-process sans coût d'isolation inutile.

**Local léger par défaut, isolation quand elle apporte une valeur réelle.**

### 5.4 Contrat minimum d'une capability

Chaque capability doit pouvoir déclarer au minimum :

```text
id
version
kind
provides[]
requires[]
optional_requires[]
platforms[]
configuration_schema
entrypoint
lifecycle
permissions / effects
```

Le registry produit un **graphe de services/capabilities**, jamais une liste opaque de modules.

```mermaid
flowchart LR
    A["parser.markdown"] -- provides --> DOC["document.ast"]
    B["references.csl"] -- provides --> REF["references.resolved"]
    C["renderer.docx"] -- requires --> DOC
    C -- requires --> REF
    D["profile.wust-thesis"] -- composes --> A
    D -- composes --> B
    D -- composes --> C
```

Les dépendances inter-capabilities passent par des contrats de services. Une capability ne doit pas importer les internals d'une autre capability comme API implicite.

### 5.5 Profiles / bundles — le produit comme composition

Un document publiable n'est pas un gros plugin.

```mermaid
flowchart TD
    W["profile:wust-thesis"]

    W --> MD["source.markdown"]
    W --> DISC["discovery.filesystem"]
    W --> REF["references.csl"]
    W --> FIG["assets.figures"]
    W --> EQ["equations"]
    W --> DOCX["renderer.docx"]
    W --> STYLE["style.wust"]
    W --> VAL["validator.thesis"]

    DOCX --> ART["thesis.docx"]
```

Un profile est une composition nommée, versionnée et surchargeable.

Exemples futurs :

```text
profile:wust-thesis
profile:ieee-article
profile:technical-report
profile:book
profile:web-documentation
```

Le profile décrit **ce qui est assemblé** ; il n'implémente pas lui-même toutes les capacités.

## 6. Baseline technologique candidate

Cette section fait sortir le projet des nuages sans transformer une technologie en dogme. Toute candidate doit passer par un prototype et des fitness functions avant d'être gelée par Target.

### 6.1 Runtime principal — Python 3.12+

**Python 3.12+** est la baseline candidate la plus cohérente :

- excellente lisibilité pour humains et agents IA ;
- écosystème documentaire mature ;
- compatibilité directe avec une grande partie des connaissances acquises via MDDOCX sans conserver son architecture ;
- SDK MCP officiel ;
- packaging/plugin discovery standards ;
- cross-platform Windows/Linux/macOS ;
- coût opérationnel faible.

Le domaine du kernel doit privilégier la bibliothèque standard :

```text
dataclasses
typing.Protocol
pathlib
graphlib
hashlib
importlib.metadata
```

`Pydantic` intervient surtout **aux frontières** : manifestes, configuration, protocoles externes, sérialisation et validation d'inputs. Le domaine interne ne doit pas en devenir dépendant sans nécessité.

### 6.2 Packaging et monorepo — uv workspace

```mermaid
flowchart TD
    ROOT["MDForge workspace<br/>pyproject.toml + uv.lock"]
    ROOT --> K["packages/kernel"]
    ROOT --> C["packages/contracts"]
    ROOT --> A["packages/application"]
    ROOT --> CLI["packages/cli"]
    ROOT --> MCP["packages/mcp"]
    ROOT --> PL["packages/plugins/*"]
    ROOT --> PF["packages/profiles/*"]
```

`uv workspace` est la baseline candidate pour :

- un lockfile commun ;
- des packages réellement séparés ;
- des dépendances explicites ;
- une installation rapide ;
- une granularité favorable aux agents parallèles.

### 6.3 Découverte de plugins — standards Python

La première couche de découverte doit utiliser les **Python package entry points** via `importlib.metadata.entry_points()`.

Exemple conceptuel :

```toml
[project.entry-points."mdforge.capabilities"]
markdown = "mdforge_markdown:plugin"
docx = "mdforge_docx:plugin"
```

Ainsi un plugin peut vivre :

```text
dans le monorepo
dans un repository séparé
sur un index Python
comme package installé explicitement par l'Operator
```

### 6.4 Hooks — pluggy comme candidate, pas comme kernel

`pluggy` est une candidate adaptée aux hooks 1→N et à la validation d'implémentations.

Mais :

> **un hook system n'est pas un plugin runtime complet.**

Le graphe de services, le lifecycle, la résolution des dépendances, l'isolation, les Build Plans et les permissions restent des responsabilités MDForge.

### 6.5 Concurrence — AnyIO

`AnyIO` est le candidat pour :

- concurrence structurée ;
- annulation ;
- orchestration async portable.

Les conversions lourdes CPU/processus restent explicitement exécutées comme subprocess ou workers. MDForge ne doit pas rendre l'ensemble du domaine async « par principe ».

### 6.6 CLI — Typer + Rich

Baseline candidate :

```text
Typer
+ Rich
```

Objectifs :

- commandes typées ;
- aide et completion automatiques ;
- diagnostics lisibles ;
- progress/status sans bruit ;
- sortie JSON structurée pour agents/automatisations.

Surface cible :

```text
mdforge build .
mdforge doctor
mdforge plugins
mdforge inspect
mdforge plan
mdforge explain last
```

### 6.7 HTTP local — FastAPI optionnel

Si une UI web ou une intégration HTTP locale est retenue, **FastAPI** est un candidat naturel comme adapter au-dessus de l'Application API.

FastAPI n'est pas requis pour :

```text
CLI
headless build
SDK Python
MCP stdio
```

Le produit doit rester utilisable sans serveur.

### 6.8 MCP — SDK Python officiel

MCP est un **adapter**, pas une seconde architecture.

Le SDK Python MCP officiel est la baseline candidate.

```text
MCP tool "build"
      ↓
Application API.build()
      ↓
same Build Plan
      ↓
same BuildRecord
```

CLI, UI et MCP doivent donc produire les mêmes effets applicatifs pour la même intention et la même configuration.

### 6.9 Qualité d'ingénierie

Baseline candidate :

```text
pytest
Ruff
type checking strict
contract tests
integration tests
acceptance fixtures
```

Les tests platform-specific (Word COM, OS adapters) doivent être séparés du corpus headless.

## 7. Topologie data minimale, locale et transparente

Le contenu utilisateur ne doit jamais disparaître dans une base opaque.

```mermaid
flowchart LR
    SRC["User Sources<br/>Markdown / assets / references"]
    CFG["mdforge.toml<br/>versionné"]
    DB["SQLite<br/>operational state"]
    CAS["Artifact Store<br/>content-addressed"]
    LED["Build Ledger"]

    SRC --> BUILD["Build"]
    CFG --> BUILD
    DB --> BUILD
    BUILD --> CAS
    BUILD --> LED
```

### 7.1 Sources et configuration canonique

Fichiers utilisateur + `mdforge.toml` :

- lisibles ;
- portables ;
- versionnables ;
- éditables sans outil propriétaire.

### 7.2 État opérationnel local

**SQLite** est la baseline candidate pour :

- catalogue/cache ;
- historique des builds ;
- état des plugins ;
- diagnostics ;
- index/fingerprints.

Avantages recherchés :

```text
embedded
transactional
zero-server
cross-platform
inspectable
backup simple
```

SQLite ne devient jamais la source de vérité des contenus auteurs.

### 7.3 Artifacts

Filesystem content-addressable store, adressé par SHA-256 :

```text
outputs
snapshots
intermediates utiles
evidence
```

Un Build Record référence les hashes au lieu de dupliquer le contenu.

### 7.4 Build reproductible

Un build doit pouvoir être décrit comme :

```text
Build =
    SourceSnapshot
  + ProjectConfiguration
  + ProfileComposition
  + CapabilityVersions
  + ToolchainFingerprint
  + BuildRequest
```

Résultat :

```text
BuildRecord
├── build_id
├── input_fingerprint
├── capability_graph
├── resolved_profile
├── toolchain
├── warnings/errors
├── output_artifacts
└── evidence
```

L'explicabilité n'est donc pas une fonction UI. C'est une propriété du backend.

## 8. Expectations produit

MDForge mature devrait permettre, sans réarchitecture, de satisfaire des intentions comme :

```text
« Voici ce dossier Markdown ; comprends sa structure. »
« Forge-le comme thèse WUST en DOCX. »
« Forge le même contenu comme rapport interne. »
« Produit une candidate Word sans toucher au master. »
« Donne-moi HTML + PDF à partir du même graphe documentaire. »
« Explique pourquoi ce build échoue. »
« Quelles capabilities manquent pour cette recette ? »
« Recompile uniquement ce qui a changé. »
« Montre-moi exactement quelles sources ont produit cet artefact. »
« Installe ce renderer et utilise-le dans ce profile sans patcher le kernel. »
```

### Expectations constitutionnelles

1. **Composable** — des capacités peuvent être ajoutées/remplacées sans patcher le kernel.
2. **Contract-first** — version, compatibilité et limites d'un plugin sont explicites et testables.
3. **Project-aware** — la forge comprend un projet, pas seulement une liste de fichiers.
4. **Graph-aware** — structure, références, assets et relations deviennent un modèle explicite.
5. **Profile-aware** — conventions de publication séparées du renderer.
6. **Multi-output** — un même projet peut produire plusieurs artefacts.
7. **Reproductible** — inputs, config, versions, capabilities et artefacts sont traçables.
8. **Inspectable** — plan de build et diagnostics sont visibles avant/après exécution.
9. **Incremental-ready** — l'architecture ne doit pas empêcher cache, fingerprints et builds différentiels.
10. **Safe** — candidates/snapshots par défaut pour les artefacts autoritaires.
11. **Headless-first** — le cœur fonctionne sans GUI.
12. **Human + agent parity** — humains et agents passent par les mêmes cas d'usage applicatifs.
13. **Portable** — la logique documentaire ne doit pas être prisonnière de Windows/Word, même si certaines capabilities le sont.
14. **Observable** — erreurs structurées, événements et provenance plutôt que traces opaques.
15. **Testable in isolation** — contracts, fixtures et doubles permettent de tester une capability sans toute la forge.
16. **Local-first** — aucune infrastructure serveur ne doit être nécessaire pour le happy path.
17. **Externally extensible** — un logiciel existant peut être enveloppé comme capability au lieu d'être réécrit.
18. **Agent-parallel friendly** — deux capabilities indépendantes peuvent évoluer en parallèle sans conflit structurel récurrent.

## 9. Modèle mental du produit

```mermaid
flowchart LR
    P["Project Spec"] --> S["Source Graph"]
    S --> D["Document Graph"]
    D --> C["Capability Graph"]
    C --> B["Build Plan"]
    B --> R["Build Run"]
    R --> A["Artifact Set"]
    R --> E["Build Record / Evidence"]
```

### Séparations essentielles

```text
fichiers physiques          ≠ unités documentaires
ordre des fichiers          ≠ structure logique
profile                     ≠ capability
profil de publication       ≠ format de sortie
renderer                    ≠ post-processing
configuration utilisateur   ≠ état runtime
cache                       ≠ source de vérité
logs                        ≠ preuve structurée
MCP                         ≠ application core
plugin                      ≠ package Python obligatoire
```

## 10. Human-native, agent-native et UX par construction

L'objectif n'est pas de construire plusieurs produits.

```mermaid
flowchart TD
    CLI["CLI — reference surface"] --> APP["Application API"]
    UI["Desktop/Web UI"] --> APP
    SDK["Python SDK"] --> APP
    MCP["MCP Adapter"] --> APP
    AUTO["Automation / Agents"] --> APP

    APP --> K["Microkernel + Capabilities"]
```

Aucune surface ne doit posséder de logique documentaire divergente.

### CLI

La CLI sert de **surface de référence headless** :

```text
simple pour l'humain
stable pour les scripts
structurée pour les agents
```

Chaque commande importante doit avoir une sortie humaine et, quand pertinent, une sortie machine stable (`--json` ou équivalent).

### UI

L'UI doit être un client mince de l'Application API.

Elle pourra proposer :

```text
project cockpit
capability/profile explorer
build plan preview
artifact browser
diagnostics/action center
visual comparison of builds
```

Sa technologie finale reste à choisir après prototype UX.

### MCP

Un agent doit pouvoir :

- inspecter un projet ;
- découvrir les capabilities disponibles ;
- obtenir un Build Plan sans exécuter ;
- lancer un build autorisé ;
- recevoir événements et diagnostics structurés ;
- localiser l'artefact et sa provenance ;
- comprendre les actions correctives sans parser une UI ou une traceback.

## 11. Topologie de repository favorable aux réseaux d'agents

Baseline candidate :

```text
Mdforge/
├── pyproject.toml
├── uv.lock
├── packages/
│   ├── kernel/
│   ├── contracts/
│   ├── application/
│   ├── cli/
│   ├── mcp/
│   ├── web/                 # seulement si retenu
│   ├── plugins/
│   │   ├── source-markdown/
│   │   ├── parser-markdown/
│   │   ├── references-csl/
│   │   ├── renderer-docx/
│   │   ├── validator-core/
│   │   └── ...
│   └── profiles/
│       ├── wust-thesis/
│       └── ...
├── tests/
│   ├── contracts/
│   ├── integration/
│   └── acceptance/
└── _/agents/
```

```mermaid
flowchart LR
    A1["Agent A<br/>renderer.docx"] --> CT["Stable Contracts"]
    A2["Agent B<br/>references.csl"] --> CT
    A3["Agent C<br/>CLI"] --> API["Application API"]
    A4["Agent D<br/>MCP"] --> API
    A5["Agent E<br/>profile WUST"] --> CT

    CT --> K["Kernel"]
    API --> K
```

### Fitness functions agentiques

- aucune importation plugin→plugin par implémentation ;
- aucun renderer connu du kernel ;
- contract tests obligatoires par capability ;
- manifest valide ;
- dépendances résolubles ;
- build déterministe sur fixture ;
- sortie structurée stable ;
- installation/retrait d'une capability testés ;
- rollback lifecycle testé ;
- corpus headless séparé des tests platform-specific ;
- changement d'un plugin n'oblige pas à toucher le kernel sauf évolution explicite du contrat.

L'objectif est de réduire le **conflict surface area** pour les agents autant que la complexité logicielle.

## 12. Déploiement — léger par défaut

MDForge doit pouvoir être utile avec :

```text
un runtime local
+ les capabilities réellement nécessaires
+ zéro service obligatoire
```

### Happy path

```text
install
→ mdforge doctor
→ mdforge build .
```

Aucun daemon, base distante ou orchestrateur externe ne doit être requis.

### Extensions possibles

```text
local HTTP adapter
desktop wrapper
remote build worker
daemon
shared artifact service
```

Ces extensions doivent être optionnelles et se brancher sur les mêmes contrats.

La distribution finale (package Python, standalone executable, desktop bundle) reste à comparer par Target.

## 13. Relation constitutionnelle avec MDDOCX — migration totale puis retrait

La cible n'est plus de préserver MDDOCX comme plugin géant.

MDDOCX doit être traité comme :

```text
laboratoire historique de besoins
+ oracle de comportements
+ collection de cas limites / fixtures
+ source d'exigences DOCX/Word
≠ architecture à conserver
≠ dependency permanente
≠ capability monolithique finale
```

### Stratégie cible

```mermaid
flowchart LR
    OLD["MDDOCX legacy"] --> INV["Behavior / parity inventory"]
    INV --> CAPS["MDForge capabilities"]
    CAPS --> PROOF["Parity + improved UX"]
    PROOF --> RETIRE["Retrait MDDOCX"]
```

Principes :

1. caractériser les comportements utiles avant remplacement ;
2. reclasser chaque fonction utile dans la capability correcte ;
3. ne pas déplacer mécaniquement l'architecture hexagonale existante ;
4. préserver les fixtures et cas limites utiles ;
5. prouver parité fonctionnelle + meilleure UX ;
6. retirer le submodule et les voies MDDOCX quand aucune autorité active n'en dépend ;
7. archiver les preuves de migration selon les règles TAKOUDJOU.

Les particularités Word pourront survivre sous forme de capabilities dédiées (`renderer.docx`, `platform.word-com`, etc.), mais **MDDOCX comme produit autonome est destiné à disparaître** si la migration atteint sa preuve de parité.

## 14. Topologies encore ouvertes

Le Memory Diagram choisit maintenant une **baseline technologique crédible**, mais laisse volontairement ouvertes les décisions qui nécessitent prototype ou benchmark.

| Axe | Baseline / question restante |
|---|---|
| **Kernel** | Python 3.12+ ; préciser la frontière exacte kernel/application/planner |
| **Plugin runtime** | entry points + in-process par défaut ; définir isolation subprocess/service et lifecycle |
| **Hooks** | évaluer `pluggy` uniquement là où les hooks apportent une vraie valeur |
| **Frontend** | CLI référence ; comparer desktop native, web local et wrapper hybride |
| **Data** | SQLite + filesystem CAS ; définir schema, GC, migrations et layering |
| **Configuration** | `mdforge.toml` ; préciser profiles, overrides locaux, secrets et portable paths |
| **MCP** | SDK officiel ; préciser tools/resources, streaming, permissions et long-running builds |
| **Distribution** | `uv`/package Python comme dev baseline ; comparer standalone executable/desktop bundle |
| **Security** | définir trust model, filesystem/network/process scopes et sandbox des plugins externes |
| **Cross-language** | définir si/à quel moment un wire protocol stable devient nécessaire |
| **Workers distants** | hors happy path ; seulement si les workloads le justifient |

Les choix définitifs doivent être arbitrés par :

```text
expectations
+ prototype
+ benchmark
+ fitness functions
+ coût de maintenance
+ expérience Operator
+ expérience agent
```

## 15. Frontières de responsabilité cibles

```text
MDForge Microkernel
  possède discovery, contracts, service context, lifecycle, composition primitives

Application Core
  possède les cas d'usage et orchestration métier générique

Build Planner
  résout un projet + capability graph en Build Plan inspectable

Project Model
  possède l'intention documentaire déclarative et le graphe résolu

Capabilities
  possèdent le traitement spécialisé

Profiles / Bundles
  composent des capabilities et de la configuration

Renderers
  matérialisent un format

Build Ledger
  possède Build Records, provenance et evidence references

Surfaces
  possèdent interaction, jamais les règles métier centrales

MCP
  possède traduction protocolaire agent ↔ Application API
```

## 16. Familles de Targets qui doivent naître de cette carte

Ce sont des frontières de futurs programmes, pas encore leurs plans d'implémentation :

1. **Foundation & Microkernel Contracts** — capability contract, registry, service context, lifecycle, errors/events.
2. **Project & Document Graph** — project spec, discovery, source/document model, références/assets.
3. **Plugin Runtime & Composition** — entry points, manifests, dependency resolution, profiles/bundles, isolation.
4. **Build Engine & Evidence** — planner, execution, incremental/cache strategy, build record, artifact store, diagnostics.
5. **Human Experience** — CLI référence puis meilleure surface interactive, preview et ergonomie projet.
6. **Agent/MCP Surface** — discovery, inspection, planning, build, diagnostics, permissions et long-running work.
7. **Legacy Extraction & MDDOCX Retirement** — inventory, fixtures, parity, migration, retrait du submodule.

Ces familles pourront être fusionnées ou scindées après les exercices de topologie. Le présent diagramme ne fixe pas leur nombre final.

## 17. Invariants constitutionnels

1. Le kernel reste petit ; une exception demande une justification architecturale.
2. Tout ce qui varie par type de document, format, outil externe ou workflow est candidat à une capability.
3. Une capability peut être native, exécutable, service, MCP ou platform adapter ; « plugin » n'implique pas Python.
4. Un plugin ne lit pas les internals d'un autre plugin comme API implicite.
5. Les contrats partagés sont versionnés et testables.
6. Publication Profile et Output Renderer restent orthogonaux.
7. Le modèle documentaire interne ne dépend pas des noms de dossiers.
8. Les effets filesystem/process/network sont gouvernés par des ports/adapters identifiables.
9. Un build peut être planifié et inspecté avant exécution.
10. Les surfaces UI/CLI/MCP n'embarquent pas de logique métier divergente.
11. L'écrasement d'un artefact autoritaire est explicite, jamais le défaut.
12. L'état dérivé/cache est reconstructible ; l'input autoritaire est identifiable.
13. Une capability optionnelle peut être absente sans rendre le kernel inutilisable.
14. Une panne de plugin produit un diagnostic borné et attribuable.
15. Le happy path reste local-first et sans serveur obligatoire.
16. Une capability significative peut être ajoutée sans patcher le kernel.
17. La modularité est mesurée par les frontières et remplaçabilités réellement testées, pas par le nombre de dossiers `modules/`.
18. MDDOCX est une source de migration temporaire, pas une dépendance architecturale permanente.
19. Les frontières du repository doivent permettre le travail parallèle d'agents sans conflits structurels récurrents.
20. Un choix technologique n'est gelé qu'après prototype et preuve adaptée.

## 18. Test du théorème

Le théorème est réellement implémenté lorsqu'une nouvelle capacité significative peut être ajoutée sans modifier le kernel.

```text
Given:
  MDForge installé et fonctionnel

When:
  un nouveau renderer / parser / validator / source provider est installé

Then:
  il est découvert,
  son contrat est validé,
  ses dépendances sont résolues,
  il apparaît dans le capability graph,
  un profile peut le composer,
  CLI/UI/MCP peuvent l'utiliser via l'Application API,
  un Build Record permet d'expliquer l'exécution,
  et son retrait restaure proprement l'état précédent

Without:
  patcher le kernel.
```

Cette propriété — et non le nombre de formats déjà supportés — prouve que MDForge est réellement devenu une forge modulaire.

## 19. Contrôle avant toute mission d'implémentation

Avant de rédiger un premier Target de code, répondre explicitement :

```text
1. Quelle expectation produit cette cible sert-elle ?
2. Quelle frontière devient stable après cette cible ?
3. Qu'est-ce qui doit rester remplaçable ?
4. Quel contrat peut être gelé sans choisir trop tôt la topologie ?
5. Quelle partie de MDDOCX est seulement caractérisée puis migrée ?
6. Quelle preuve démontrera la modularité réelle ?
7. Le chemin humain et le chemin agent consomment-ils la même Application API ?
8. L'état et les artefacts produits sont-ils traçables et reconstructibles ?
9. Le changement peut-il être développé/testé par un agent sans toucher des modules indépendants ?
10. Le choix technologique est-il justifié par prototype/benchmark ou seulement par préférence ?
```

Si une cible force plusieurs topologies non encore prouvées en même temps, elle est trop couplée et doit être redécoupée.

## 20. Cycle de vie

Ce diagramme reste actif tant qu'il gouverne l'architecture de MDForge. Les futurs Targets le référencent dans `source_context`.

Une évolution majeure produit une nouvelle version avec `supersedes` et met à jour les références dans le même commit. Il n'est archivé que lorsqu'aucun Target, skill ou document actif n'en dépend.

## 21. Résultat mental final

```mermaid
flowchart TD
    SRC["Markdown + assets + refs"]
    PROJ["Project Model"]
    PROF["Profile / Bundle"]
    K["MDForge Microkernel"]
    REG["Capability Graph"]
    PLAN["Build Plan"]
    RUN["Build Run"]
    ART["Artifacts"]
    REC["Build Record / Evidence"]

    SRC --> PROJ
    PROF --> K
    PROJ --> K
    K --> REG
    REG --> PLAN
    PLAN --> RUN
    RUN --> ART
    RUN --> REC
```

```text
Kernel        = composition substrate
Capabilities  = puzzle pieces
Profiles      = named compositions
Application   = common use cases
CLI/UI/MCP    = adapters
SQLite/CAS    = lightweight operational substrate
MDDOCX        = temporary migration oracle, then retired
```

> **MDForge doit rendre facile l'ajout d'un nouveau fil documentaire ou d'un logiciel existant sans obliger à redessiner la forge.**
