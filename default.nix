{ lib
, python
, pygobject3
, pycairo
, gtk3
, gobject-introspection
, wrapGAppsHook
}:
python.pkgs.buildPythonPackage rec {
  pname = "pye-menu";
  version = "1.0";
  src = ./src;
  propagatedBuildInputs = [ gtk3 pygobject3 pycairo ];
  propagatedNativeBuildInputs = [ wrapGAppsHook gobject-introspection ];

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
