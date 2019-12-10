let nixpkgs = import <nixpkgs> {};
in
{ python3 ? nixpkgs.python3,
  gtk3 ? nixpkgs.gtk3,
  gobject-introspection ? nixpkgs.gobject-introspection,
  wrapGAppsHook ? nixpkgs.wrapGAppsHook,
  lib ? nixpkgs.lib 
}:
python3.pkgs.buildPythonPackage rec {
  pname = "pye-menu";
  version = "1.0";
  src = ./.;
  propagatedBuildInputs = with python3.pkgs; [ pygobject3 pycairo ];
  nativeBuildInputs = [ wrapGAppsHook gobject-introspection ];
  buildInputs = [ gtk3 ];

  GST_PLUGIN_SYSTEM_PATH_1_0 = ''""'';
  GRL_PLUGIN_PATH = ''""'';

  strictDeps = false;

  dontWrapGApps = true;
  makeWrapperArgs = [ "\${gappsWrapperArgs[@]}" ];

  meta = with lib; {
    description = "Python library and application for makig pie menus";
    license = licenses.mit;
    maintainers = with maintainers; [ kovirobi ];
  };
}
