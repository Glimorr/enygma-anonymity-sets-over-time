#!/usr/bin/env python3
"""Verify a published Rayls Enygma release without modifying signed research.

The 93-file archive is read from its exact pre-anchor Git revision and audited
in an isolated temporary directory. Later website presentation updates and the
retrospective public Testnet receipt are validated separately. No signing keys,
Docker deployments, chain writes, or working-tree modifications are used.
"""
import argparse
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN_COMMIT = "5710488133292dfbe3ee1df3b731b198a5999031"
ARCHIVE_ROOT = "ee9338b512ab07401372ad98bf64e1103f11d212e70656b4e1d6c36f34b4e470"
ALLOWED_WEBSITE_CHANGES = {
    "index.html",
    "public-anchor.js",
    "public-anchor.json",
    "figure-viewer.js",
    "figure-viewer.css",
}

def run(args, cwd=ROOT, **kwargs):
    return subprocess.run(args, cwd=cwd, check=True, **kwargs)

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-only", action="store_true",
        help="Audit frozen manifest, approved website updates, and annex metadata; skip extended reproduction tests."
    )
    parser.add_argument(
        "--live-rpc", action="store_true",
        help="Also verify the publicly mined Testnet receipt against the Rayls RPC."
    )
    args = parser.parse_args()
    require((ROOT / "EVIDENCE-MANIFEST.json").is_file(), "Public research manifest missing.")
    require((ROOT / "site/public-anchor.json").is_file(), "Verified public receipt annex missing.")
    require((ROOT / ".git").exists(), "A full Git checkout with archived revision history is required. Clone the public repository.")
    run(["git", "cat-file", "-e", FROZEN_COMMIT+"^{commit}"], stdout=subprocess.DEVNULL)
    run(["git", "merge-base", "--is-ancestor", FROZEN_COMMIT, "HEAD"])
    archived=run(["git", "archive", "--format=tar", FROZEN_COMMIT], capture_output=True).stdout

    with tempfile.TemporaryDirectory(prefix="rayls-w2-immutable-archive-") as tmp:
        frozen=pathlib.Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(archived),mode="r:") as tar:
            for member in tar:
                dest=frozen / member.name
                require(dest.resolve().is_relative_to(frozen.resolve()), "Unsafe archive path.")
                require(member.isfile() or member.isdir(), "Archive contains unsupported links.")
            tar.extractall(frozen, filter="data")

        manifest=json.loads((frozen/"EVIDENCE-MANIFEST.json").read_text())
        require(manifest["files_merkle_equivalent_sha256"]==ARCHIVE_ROOT, "Frozen digest differs from committed archival root.")
        require(len(manifest["files"])==93, "Frozen file count changed.")
        require(
            (ROOT/"EVIDENCE-MANIFEST.json").read_bytes()==(frozen/"EVIDENCE-MANIFEST.json").read_bytes(),
            "Published manifest differs from the original frozen manifest."
        )
        run([sys.executable,"qa/check_manifest.py"],cwd=frozen)
        print("IMMUTABLE_93_FILE_EVIDENCE_ARCHIVE_PASS", FROZEN_COMMIT[:8],flush=True)

        frozen_site=frozen/"site"
        current_site=ROOT/"site"
        frozen_set={p.relative_to(frozen_site).as_posix() for p in frozen_site.rglob("*") if p.is_file()}
        current_set={p.relative_to(current_site).as_posix() for p in current_site.rglob("*") if p.is_file()}
        require(current_set-frozen_set <= ALLOWED_WEBSITE_CHANGES, "Unreviewed new site files: "+str(sorted(current_set-frozen_set)))
        require(frozen_set-current_set == set(), "Original site asset missing: "+str(sorted(frozen_set-current_set)))
        for name in sorted(frozen_set-ALLOWED_WEBSITE_CHANGES):
            require(
                (frozen_site/name).read_bytes()==(current_site/name).read_bytes(),
                "Frozen site research asset changed outside authorized presentation annex: "+name
            )
        run([sys.executable,"qa/check_public_copy.py",str(frozen)])
        print("POST_RELEASE_SITE_DATA_AND_COPY_SEPARATION_PASS",flush=True)

        run([sys.executable, "qa/check_anchor.py"]+(["--live-rpc"] if args.live_rpc else []))
        print("RETROSPECTIVE_PUBLIC_TESTNET_ANCHOR_PASS",flush=True)

        if not args.manifest_only:
            for command in [
                ["qa/verify_public.py"],
                ["qa/verify_local_live.py","--check-only"],
                ["qa/check_site.py","--check-only"],
                ["qa/adversarial_checks.py"],
                ["qa/check_manifest.py"],
            ]:
                if command[0]=="qa/check_site.py":
                    audit=run([sys.executable,*command],cwd=frozen,capture_output=True,text=True)
                    require("SITE_EVIDENCE_AND_ACCESSIBILITY_STATIC_AUDIT_PASS" in audit.stdout,
                            "Historical archive site-data audit did not pass.")
                    print("FROZEN_SITE_DATA_AUDIT_PASS (historical pre-anchor snapshot)",flush=True)
                else:
                    run([sys.executable,*command],cwd=frozen)
            print("NATIVE_OBSERVATIONS_LOCAL_HUB_AND_ADVERSARIAL_TESTS_PASS",flush=True)

    print("PUBLISHED_RESEARCH_VERIFICATION_PASS; original archive unmodified",flush=True)

if __name__=="__main__":
    main()
