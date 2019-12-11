let nixpkgs = import <nixpkgs> {};
in
{ python3 ? nixpkgs.python3
, gtk3 ? nixpkgs.gtk3
, gobject-introspection ? nixpkgs.gobject-introspection
, wrapGAppsHook ? nixpkgs.wrapGAppsHook
, lib ? nixpkgs.lib
}:
python3.pkgs.buildPythonPackage rec {
  pname = "pye-menu";
  version = "1.0";
  src = ./src;
  propagatedBuildInputs = with python3.pkgs; [ pygobject3 pycairo ];
  propagatedNativeBuildInputs = [ wrapGAppsHook gobject-introspection ];
  buildInputs = [ gtk3 ];

  strictDeps = false;

  preFixup = ''
    makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
  '';

  meta = with lib; {
    description = "Python library and application for makig pie menus";
    license = licenses.mit;
    maintainers = with maintainers; [ kovirobi ];
  };
}
