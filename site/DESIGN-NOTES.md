# Experience design and evidence integrity

**Project:** Enygma Longitudinal Privacy — independent Rayls research site  
**Design brief:** a cinematic editorial research experience, not a simulated financial dashboard.

## Original visual system

The design uses a dark-plum canvas, Rayls-inspired lavender / acid-lime accents, typographic hierarchy, restrained neon accents, luminous ring geometry, floating bank nodes, and compact scientific visualizations. The animated elements were written specifically for this project, not copied from template sites.

We studied current award-winning interactive patterns and their trade-offs, including:

- [Tabasco — scroll-driven 3D case study](https://hilostudiolab.com/en/projects/tabasco): one clear three-act narrative, scene progression tied to scroll, mobile usability.
- [Site of the Day teardowns](https://rickcreates.com/): purposeful visual concept and interaction, not maximal animation.
- [Awwwards 2026 reference discussion](https://www.awwwards.com/): editorial typography, perspective, controlled transitions and hover feedback.

No external fonts, copied models, website templates, stock hero assets, external animation libraries, analytics or tracking scripts are required for the site to function.

## What moves — and why

| Motion component | Purpose | Evidence classification |
|---|---|---|
| Floating bank orbit | Illustrate a six-bank set, not a real payment | Decorative |
| Scroll-driven 3D Hub | Explain single observation → repeated membership → blind analysis | Illustrative |
| Kinetic hero typography | Establish the research question | Editorial |
| Floating evidence tags | Establish known local-network and observation counts | Based on verified study |
| Chapter rail and reading progress | Navigate a long technical article | Interface |
| Animated source bars | Show measured native selection frequencies | Native/source-level |
| Clickable Hub membership lens | Filter six actual local Hub receipts by bank ID | Real local-chain data |
| Original six SVG figures | Document architecture, controls, settlement and Hub membership | Appropriately labeled |

## Site data rules

The six local Hub rows come from `evidence/local-live-seven/receipt-reconciliation.json`, decoded and rechecked against local RPC in our research environment. **Anonymity-set inclusion is not proof that a bank received money.** Native relayer tests use synthetic schedules and remain distinct from chain receipts.

All real-chain claims refer only to the researcher-controlled local seven-bank stack, not independently governed external consensus. No Rayls Public Testnet anchor is reported until its own mined receipt can be independently verified.

## Performance and accessibility

- Progressive HTML, CSS 3D transforms and dependency-free canvas: no WebGL framework or third-party JS payload.
- The site runs from local files for reproduction and from GitHub Pages after publication.
- A **Pause motion** control and `prefers-reduced-motion` CSS are supported.
- Keyboard-accessible bank controls, labeled data charts, copyable transaction hashes, meaningful image alternatives, visible focus indicators.
- At smaller viewports the 3D narrative stacks into a normal flow; the observed Hub table can scroll horizontally without forcing the whole page wider.
- The mobile hero disables its blur-based word reveal to remain readable even during slow rendering.

## Quality assurance

- The standalone static audit checks all internal links, local assets, six figure files, receipt-derived bank sets, exact balance accounting and provenance labeling.
- Desktop browser scripts exercised the bank lens, six transaction-batch selectors, chart range controls and motion pause/resume.
- Tested 1440px desktop, 744px tablet CSS viewport, and Edge's minimum headless viewport of approximately 492px. The tablet overflow was fixed.
- Screenshot captures and browser interaction logs are retained locally for editorial review. Browser QA does not independently prove underlying ledger history.

The site is intentionally evidence-led: visual polish must never turn an illustrative privacy mechanism into a claimed real-world attack.
