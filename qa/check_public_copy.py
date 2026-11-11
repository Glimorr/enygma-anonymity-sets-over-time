#!/usr/bin/env python3
"""Enforce presentation-only public copy changes relative to frozen research.

This never alters the 93-file evidence archive pinned at pre-anchor SHA.
The current public website may use clearer wording but must retain its
scientific content, citations, DOM structure and original visual effects.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) not in (2,3):
    raise SystemExit("Usage: check_public_copy.py <frozen-research-checkout> [--apply]")
FROZEN=Path(sys.argv[1])
PATH=Path("site/index.html")
original=(FROZEN/PATH).read_text(encoding="utf-8")
replacements=[
 ('content="Interactive Rayls Enygma research: 5,000 native observations, blind controls, genuine seven-bank local Hub receipts, six decoded batches, 3D visualizations and reproducible evidence."',
  'content="Independent Rayls Enygma research: 5,000 native observations, blind controls, genuine seven-bank local Hub receipts, six decoded batches and reproducible evidence."'),
 ('<a href="#journey">3D walkthrough</a>', '<a href="#journey">Privacy model</a>'),
 ('Public Testnet evidence commitments remain pending.', 'The final research archive hash was retrospectively committed on Rayls Public Testnet.'),
 ('aria-label="Decorative three-dimensional bank network visualization"', 'aria-label="Illustration of participant banks in an Enygma anonymity set"'),
 ('aria-label="Scroll-driven protocol visualization"', 'aria-label="Protocol observer-model illustration"'),
 ('02 / A privacy question in three dimensions', '02 / How repeated payments leave metadata'),
 ("Scroll through the protocol illustration, then inspect the real native experiment data below. This 3D sequence illustrates the observer model—it is not a captured transaction.",
  "Follow how anonymity-set membership changes across repeated transfers, then inspect the native measurements below. This schematic shows the observer model; it is not a transaction receipt."),
 ('aria-label="Illustrative 3D bank network, not experimental evidence"', 'aria-label="Illustration of seven bank participants and a private network hub; not transaction evidence"'),
 ("Five original diagrams, grounded in actual observations.", "Six original diagrams, grounded in actual observations."),
 ('<div class="code-head">VERIFICATION COMMANDS • FROM RESEARCH REPOSITORY ROOT</div>',
 '''<div class="code-head">VERIFY THE PUBLISHED RESEARCH</div>
<p class="description">From a current Git checkout, one command checks the original <a href="https://github.com/Glimorr/enygma-anonymity-sets-over-time/tree/5710488133292dfbe3ee1df3b731b198a5999031" target="_blank" rel="noopener">93-file research archive (revision 5710488)</a>, the separately published website enhancements and the retrospective Rayls Public Testnet receipt. The original signed archive remains unchanged.</p>'''),

 ('<pre><code>python3 qa/check_manifest.py\npython3 qa/verify_local_live.py --check-only\npython3 qa/verify_public.py\npython3 qa/adversarial_checks.py', '<pre><code>python3 qa/verify_published_release.py --live-rpc\n\n# Offline verification (no public-chain RPC required)\npython3 qa/verify_published_release.py\n\n# Optional direct checks\npython3 qa/verify_local_live.py --check-only\npython3 qa/verify_public.py\npython3 qa/adversarial_checks.py'),
 ('--output analysis/recomputed_blind_predictions.json', '--output /tmp/recomputed-enygma-w2-predictions.json'),
]
replacements.extend([
 ('<link rel="stylesheet" href="bank-lens.css"/>', '<link rel="stylesheet" href="bank-lens.css"/>\n<link rel="stylesheet" href="figure-viewer.css"/>'),
 ('<script src="public-anchor.js"></script>', '<script src="public-anchor.js"></script>\n<script src="figure-viewer.js"></script>')
])
expected=original
for old,new in replacements:
    assert expected.count(old)==1, "Frozen source changed or copy marker ambiguous: "+old[:75]
    expected=expected.replace(old,new,1)
path=ROOT/PATH
if len(sys.argv)==3:
    assert sys.argv[2]=="--apply", "Unrecognized mode"
    path.write_text(expected,encoding="utf-8")
assert path.read_text(encoding="utf-8")==expected, "Non-copy change found in public site/index.html"
for name in ("figure-viewer.css","figure-viewer.js"):
    asset=ROOT/"site"/name
    assert asset.is_file() and asset.stat().st_size>1000, "Missing figure viewer asset: "+name
assert 'role="dialog"' in (ROOT/"site/figure-viewer.js").read_text(), "Viewer missing semantic dialog"
assert "prefers-reduced-motion:reduce" in (ROOT/"site/figure-viewer.css").read_text(), "Viewer missing reduced motion"

print("PUBLIC_SITE_RESEARCH_FOCUSED_COPY_AND_FROZEN_SOURCE_VERIFIED",len(replacements))
