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
]
expected=original
for old,new in replacements:
    assert expected.count(old)==1, "Frozen source changed or copy marker ambiguous: "+old[:75]
    expected=expected.replace(old,new,1)
path=ROOT/PATH
if len(sys.argv)==3:
    assert sys.argv[2]=="--apply", "Unrecognized mode"
    path.write_text(expected,encoding="utf-8")
assert path.read_text(encoding="utf-8")==expected, "Non-copy change found in public site/index.html"
print("PUBLIC_SITE_RESEARCH_FOCUSED_COPY_AND_FROZEN_SOURCE_VERIFIED",len(replacements))
