{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let
      out = system:
        let pkgs = nixpkgs.legacyPackages."${system}";
        in
        {

          devShell = pkgs.mkShell {
            buildInputs = (with pkgs; [
              python3
              gtk3
              gobject-introspection
            ]) ++ (with pkgs.python3.pkgs; [
              pygobject3
              pycairo
              black
              isort
            ]);
          };

          packages.pye-menu = pkgs.python3.pkgs.buildPythonPackage {
            name = "pye-menu";
            src = "${self}/src";
            propagatedBuildInputs = (with pkgs; [
              python3
              gtk3
              # See https://github.com/NixOS/nixpkgs/issues/56943
              gobject-introspection
            ]) ++ (with pkgs.python3.pkgs; [
              pygobject3
              pycairo
            ]);
            propagatedNativeBuildInputs = with pkgs; [
              wrapGAppsHook
              gobject-introspection
            ];

            dontWrapGApps = true;
            preFixup = ''
              makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
            '';

            meta = with pkgs.lib; {
              description = "Python library and application for makig pie menus";
              license = licenses.mit;
              maintainers = with maintainers; [ kovirobi ];
            };
          };

          packages.pen-menu = pkgs.python3.pkgs.buildPythonApplication {
            pname = "pen-pye-menu";
            version = "1.0";

            src = "${self}/examples";

            propagatedBuildInputs = [
              self.defaultPackage.${system}
              pkgs.python3.pkgs.pycairo
            ];

            preConfigure = ''
              substituteAllInPlace pen_menu
            '';

            i3msg = "${pkgs.i3}/bin/i3-msg";
            mpc = "${pkgs.mpc_cli}/bin/mpc";
            loginctl = "${pkgs.systemd}/bin/loginctl";
            flameshot = "${pkgs.flameshot}/bin/flameshot";

            meta = with pkgs.lib; {
              description = "Example Python pie menu";
              license = licenses.mit;
              maintainers = with maintainers; [ kovirobi ];
            };
          };

          defaultPackage = self.packages."${system}".pye-menu;
          defaultApp = utils.lib.mkApp {
            drv = self.defaultPackage."${system}";
          };

        }; in
    with utils.lib; eachSystem defaultSystems out;

}
