{ nixpkgs ? import <nixpkgs> {} }:
with nixpkgs;
python3Packages.callPackage ./. {}
