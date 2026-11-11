#!/usr/bin/env python3
"""Reproduce upstream source provenance without bundling upstream repositories.

Requires Git and internet for first run. Never uploads or changes upstream.
"""
import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPOS={
  "rayls-sovereign-relayer": ("raylsnetwork/rayls-sovereign-relayer","b01b427de4cfc2ac66e75eba0d5070b73a3b137c"),
  "rayls-sovereign-cli": ("raylsnetwork/rayls-sovereign-cli","c356f9211b168c643d8f25d26df709af7dc4dd92"),
  "rayls-sovereign-contracts": ("raylsnetwork/rayls-sovereign-contracts","ed8863885c8ed5d5d317d47a34c063907192687a"),
}

def git(*args,cwd):
    return subprocess.check_output(["git",*args],cwd=cwd,text=True).strip()

def file_hash(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--no-patches",action="store_true",help="Skip experimental CLI/Hardhat extensions")
    args=ap.parse_args()
    base=ROOT/"source"
    base.mkdir(exist_ok=True)
    for name,(repo,sha) in REPOS.items():
        dest=base/name
        if not (dest/".git").exists():
            print("CLONING",repo,flush=True)
            subprocess.run(["git","clone","--depth","1","--filter=blob:none",
                            "https://github.com/"+repo+".git",str(dest)],check=True)
        head=git("rev-parse","HEAD",cwd=dest)
        if head!=sha:
            subprocess.run(["git","fetch","--depth","1","origin",sha],cwd=dest,check=True)
            subprocess.run(["git","checkout","--detach",sha],cwd=dest,check=True)
        if git("rev-parse","HEAD",cwd=dest)!=sha:
            raise RuntimeError("Pinned source mismatch for "+name)
        print("PIN_VERIFIED",name,sha)

    orig=ROOT/"experiments/observer_w2_test.go"
    target=base/"rayls-sovereign-relayer/enygma/service/observer_w2_test.go"
    if target.exists():
        if file_hash(orig)!=file_hash(target):raise RuntimeError("Non-matching native harness already present")
    else: shutil.copyfile(orig,target)
    print("NATIVE_HARNESS_INSTALLED_UNDER_OFFICIAL_PACKAGE")

    if not args.no_patches:
        for name,patch in [
           ("rayls-sovereign-cli",ROOT/"experiments/cli-seven-extension.patch"),
           ("rayls-sovereign-contracts",ROOT/"experiments/hardhat-seven.patch"),
        ]:
            dest=base/name
            test=subprocess.run(["git","apply","--reverse","--check",str(patch)],cwd=dest,capture_output=True)
            if test.returncode==0:
                print("PATCH_ALREADY_INSTALLED",name)
            else:
                subprocess.run(["git","apply","--check",str(patch)],cwd=dest,check=True)
                subprocess.run(["git","apply",str(patch)],cwd=dest,check=True)
                print("EXPERIMENTAL_PATCH_APPLIED",name,file_hash(patch))
        copied=ROOT/"experiments/hardhat.config.seven.ts"
        updated=base/"rayls-sovereign-contracts/hardhat.config.ts"
        if file_hash(copied)!=file_hash(updated):raise RuntimeError("Seven-member Hardhat config doesn't match")
        print("SEVEN_BANK_EXTENSION_PROVENANCE_PASS")

    print("UPSTREAM_BOOTSTRAP_PASS")

if __name__=="__main__":main()
