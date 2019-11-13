let nixpkgs = import <nixpkgs> {};
in
{ python3 ? nixpkgs.python3,
  gtk3-x11 ? nixpkgs.gtk3-x11,
  gobjectIntrospection ? nixpkgs.gobjectIntrospection,
  lib ? nixpkgs.lib 
}:
python3.pkgs.buildPythonPackage rec {
  pname = "pye-menu";
  version = "1.0";
  src = ./.;
  propagatedBuildInputs = with python3.pkgs; [ pygobject3 pycairo ];
  buildInputs = [ gtk3-x11 gobjectIntrospection ];

  meta = with lib; {
    description = "Python library and application for makig pie menus";
    license = licenses.mit;
    maintainers = with maintainers; [ kovirobi ];
  };
}
