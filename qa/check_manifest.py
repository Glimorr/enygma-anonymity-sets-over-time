#!/usr/bin/env python3
"""Verify completeness and authenticity of the allowlisted public evidence package.

The manifest file itself is excluded from its own entries; all other files are
listed, including website and figures. Works without external dependencies.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=ROOT/"EVIDENCE-MANIFEST.json"
    if not manifest.exists():
        raise SystemExit("MISSING_EVIDENCE_MANIFEST")
    m=json.loads(manifest.read_text(encoding="utf-8"))
    if m["schema_version"]!=1 or m["claim_scope"]!="NATIVE_SOURCE_PLUS_RESEARCHER_CONTROLLED_LOCAL_LEDGER":
        raise AssertionError("unrecognized or overstated evidence scope")
    entries=m.get("files",{})
    if not isinstance(entries,dict) or len(entries)<30:
        raise AssertionError("manifest seems incomplete")
    declared=set(entries)
    discovered=set(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(ROOT).parts
        and "__pycache__" not in p.parts
    )
    discovered.discard("EVIDENCE-MANIFEST.json")
    if discovered!=declared:
        missing=declared-discovered
        extra=discovered-declared
        raise AssertionError("MANIFEST_COMPLETENESS_FAILED missing=%s unexpected=%s" %
                             (sorted(missing)[:25],sorted(extra)[:25]))
    for name,record in sorted(entries.items()):
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise AssertionError("noncanonical manifest path")
        p=ROOT/name
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if record["sha256"]!=h or record["bytes"]!=p.stat().st_size:
            raise AssertionError("MANIFEST_INTEGRITY_FAILED "+name)
    raw=b"".join((k+"\0"+entries[k]["sha256"]+"\n").encode() for k in sorted(entries))
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=m["files_merkle_equivalent_sha256"]:
        raise AssertionError("manifest digest mismatch")
    print("PUBLIC_MANIFEST_INTEGRITY_AND_COMPLETENESS_PASS")
    print("FILE_COUNT",len(entries))
    print("DIGEST",digest)
    print("CLAIMS_SCOPE",m["claim_scope"])

if __name__=="__main__":
    if (ROOT/"site/public-anchor.json").is_file() and (ROOT/".git").exists():
        import subprocess,sys
        print("POST_RELEASE_CHECKOUT: verifying the frozen evidence and later public annex separately",flush=True)
        subprocess.run([sys.executable,str(ROOT/"qa/verify_published_release.py"),"--manifest-only"],check=True)
    else:
        main()
