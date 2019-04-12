with import <nixpkgs> {};
stdenv.mkDerivation rec {
  name = "pye-menu";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = [
    (python35.withPackages (p: [ p.pygobject3 p.pycairo ]))
    gtk3-x11
    gobjectIntrospection
  ];
}
