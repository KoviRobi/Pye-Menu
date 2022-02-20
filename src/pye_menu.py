import subprocess  # For ExecMenuItem
from collections import defaultdict
from math import atan2, cos, pi, sin, sqrt

import cairo
import gi

gi.require_versions({"Gtk": "3.0", "PangoCairo": "1.0"})
from gi.repository import Gdk, Gtk, Pango, PangoCairo


class FontCache(dict):
    def __missing__(self, key):
        self[key] = Pango.FontDescription.from_string(key)
        return self[key]


font_cache = FontCache()


class MenuItem:
    def __init__(self, label, action=None):
        self.label = label
        self._layout = None
        self.action = action or MenuItem.get_label

    def set_label(self, label):
        self.label = label

    def get_label(self):
        return self.label

    def set_index(self, index):
        self.index = index

    def get_index(self):
        return self.index

    def add_centred_text(self, cairo, pango, x, y):
        # Text
        layout = Pango.Layout(pango)
        layout.set_font_description(font_cache["sans-serif 12"])
        layout.set_markup(self.label)
        w, h = layout.get_pixel_size()
        cairo.move_to(x - w / 2, y - h / 2)
        PangoCairo.show_layout(cairo, layout)


class ExecMenuItem(MenuItem):
    """Executes a command (by default shell=False), when this menu
    item is selected. Use shlex.quote() to escape strings! Returns
    a subprocess.CompletedProcess instance, or the raised exception.
    Example use
        ExecMenuItem("Power off", ["systemctl", "poweroff"])
    """

    def __init__(self, label, command, shell=False):
        super().__init__(label, action=ExecMenuItem.exec_command)
        self.command = command
        self.shell = shell

    def exec_command(self):
        try:
            return subprocess.run(self.command, self.shell)
        except Exception as e:
            return e


class PyeMenu(Gtk.Window):
    """Creates a pie menu, with items going from top clockwise (by
    default, because rotate is -90 by default)
    """

    def __init__(
        self,
        *args,
        action_handler=None,  # default_action_handler
        width=None,
        height=None,
        rotate=-90,
        radius=200,
        cancel_radius=50,
        accept_radius=None,
        alpha="#ffffff00",
        fg="#657b83",
        bg="#fdf6e3",
        border="#657b83",
        hi_fg="#22aa22",
        hi_bg="#cceecc",
        cancel="#fdf6e3",
        hi_cancel="#aa2222",
        accept="#eee8d5"
    ):
        super().__init__()
        keyword_args = {k: v for k, v in locals().items() if k not in ["self", "args"]}
        self.__dict__.update(keyword_args)
        self.canonicalize_colors()
        if self.action_handler is None:
            self.action_handler = PyeMenu.default_action_handler
        if self.accept_radius is None:
            self.accept_radius = self.radius + 50
        if self.width is None:
            self.width = 2 * max(self.radius, self.accept_radius)
        if self.height is None:
            self.height = 2 * max(self.radius, self.accept_radius)

        self.connect("delete-event", Gtk.main_quit)
        self.connect("destroy", Gtk.main_quit)

        self.items = []
        self.selected = None
        for arg in args:
            self.add_item(arg)

        self.set_size_request(self.width, self.height)
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.set_title("Pye Menu")
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.set_decorated(False)
        self.set_role("pye-menu")
        self.set_wmclass("pye-menu", "pye-menu")

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.do_screen_changed(None, None)

    def add_item(self, name_or_MenuItem):
        item = name_or_MenuItem
        if not isinstance(item, MenuItem):
            item = MenuItem(item)
        item.set_index(len(self.items))
        self.items.append(item)
        self.pye_arc = 2 * pi / len(self.items)
        self.pye_offset = float(self.rotate) * pi / 180 - self.pye_arc / 2

    def canonicalize_colors(self):
        for col in [
            "fg",
            "bg",
            "border",
            "hi_fg",
            "hi_bg",
            "cancel",
            "hi_cancel",
            "accept",
        ]:
            c = self.__dict__[col]
            if type(c) == str:
                c1 = ((int(c[a : a + 2], base=16) / 255) for a in [1, 3, 5])
                self.__dict__[col] = tuple(c1)
        self.alpha = tuple(
            (int(self.alpha[a : a + 2], base=16) / 255) for a in [1, 3, 5, 7]
        )

    def to_cartesian(self, phi, r):
        """Gives the cartesian coordinate for the passed in angular ones
        (cartesian is centered top-left, angular at the middle)
        """
        return (self.width / 2 + r * cos(phi), self.height / 2 + r * sin(phi))

    def to_angular(self, x, y):
        """Gives the angular coordinate (phi, r) for the passed in cartesian
        ones (cartesian is centered top-left, angular at the middle)
        """
        x, y = x - self.width / 2, y - self.height / 2
        return (atan2(y, x) % (2 * pi), sqrt(x ** 2 + y ** 2))

    def do_screen_changed(self, old_screen, user_args=None):
        """This ensures we use the right 'visual' which is stuff like the
        possibility for alpha in the background.
        """
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.supports_alpha = screen.is_composited()
        self.set_visual(visual or screen.get_system_visual())

    def do_draw(self, context, user_args=None):
        """This draws the pie menu."""
        # First draw background alpha
        if self.supports_alpha:
            context.set_source_rgba(*self.alpha)
            context.set_operator(cairo.OPERATOR_SOURCE)
        else:
            context.set_source_rgb(*self.alpha[:3])
        context.paint()

        # The background circle
        context.arc(self.width / 2, self.height / 2, self.radius, 0, 2 * pi)
        context.set_source_rgb(*self.bg)
        context.fill()

        # The values
        i = 0
        angle = self.pye_offset
        for item in self.items:
            self.draw_pie(context, item, i, angle)
            i += 1
            angle += self.pye_arc

        self.draw_cancel(context)
        # Stop propagating the draw event
        return True

    def do_button_release_event(self, event, user_args=None):
        self.select_and_quit()
        # Stop propagating the release
        return True

    def do_motion_notify_event(self, event, user_args=None):
        phi, r = self.to_angular(event.x, event.y)
        prev_selected = self.selected
        self.compute_selected(phi, r)
        if prev_selected != self.selected:
            self.queue_draw()
        if self.radius < r and r < self.accept_radius and self.selected is not None:
            self.select_and_quit()
        # Stop propagating the motion
        return True

    def compute_selected(self, phi, r):
        if self.cancel_radius < r and r < max(self.radius, self.accept_radius):
            if r < self.radius:
                angle = phi - self.pye_offset
                angle = angle % (2 * pi)
                self.selected = int(angle // self.pye_arc)
            # Else if radius < r < accept-radius, don't change
            # selected. We shouldn't set it to an int, because if the
            # user is coming from the outside (e.g. when the menu is
            # started close to the edge), then we shouldn't select and
            # accept, but give the user a chance to go into the
            # selection area and select something else. We don't want
            # to set it to None, as that would erase the user's
            # previous selection when using the accept ring.
        else:
            self.selected = None

    def select_and_quit(self):
        if self.selected is not None:
            item = self.items[self.selected]
            self.action_handler(self, item.action(item))
        else:
            self.action_handler(self, None)

    def default_action_handler(self, value):
        if value is not None:
            print(value)
        self.hide()
        self.destroy()
        Gtk.main_quit()

    def is_selected(self, i):
        return self.selected is not None and self.selected == i

    def slice_path(self, context, r, angle):
        xmid, ymid = self.to_cartesian(0, 0)
        context.move_to(xmid, ymid)
        context.line_to(*self.to_cartesian(angle, self.radius))
        context.arc(xmid, ymid, r, angle, angle + self.pye_arc)

    def draw_pie(self, context, item, i, angle):
        context.save()
        sel = self.is_selected(i)
        if self.radius < self.accept_radius:
            context.save()
            self.slice_path(context, self.accept_radius, angle)
            context.clip_preserve()
            context.set_source_rgb(*self.accept)
            context.fill_preserve()
            context.set_source_rgb(*self.border)
            context.stroke()
            context.restore()
        self.slice_path(context, self.radius, angle)
        context.clip_preserve()
        context.set_source_rgb(*(self.hi_bg if sel else self.bg))
        context.fill_preserve()
        context.set_source_rgb(*self.border)
        context.stroke()
        context.set_source_rgb(*(self.hi_fg if sel else self.fg))
        item.add_centred_text(
            context,
            self.get_pango_context(),
            *self.to_cartesian(angle + self.pye_arc / 2, self.radius / 2)
        )
        context.restore()

    def draw_cancel(self, context):
        # Cancel circle
        sel = self.selected is None
        context.new_path()
        context.arc(*self.to_cartesian(0, 0) + (self.cancel_radius, 0, 2 * pi))
        context.set_source_rgb(*(self.hi_cancel if sel else self.cancel))
        context.fill_preserve()
        context.set_source_rgb(*self.border)
        context.stroke()


class TopMenu(PyeMenu):
    """Used for the top menu in a multi-menu instance, e.g. in
       TopMenu(
         MenuItem("Foo", action=SubMenu(
             MenuItem("Bar"),
             MenuItem("Baz"))),
         MenuItem("Quux"))

    Has a convenience wrapper method 'main(self)' to replace
       win = TopMenu(
               MenuItem("Foo", action=SubMenu(
                   MenuItem("Bar"),
                   MenuItem("Baz"))),
               MenuItem("Quux"))
       win.show_all()
       Gtk.main()
    with
       TopMenu(
         MenuItem("Foo", action=SubMenu(
             MenuItem("Bar"),
             MenuItem("Baz"))),
         MenuItem("Quux")).main()
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("action_handler", TopMenu.action_handler)
        super().__init__(*args, **kwargs)

    def main(self):
        self.show_all()
        Gtk.main()

    def action_handler(self, value):
        if isinstance(value, SubMenu):
            self.selected = None
        else:
            if value is not None:
                print(value)
            self.hide()
            self.destroy()
            Gtk.main_quit()


class SubMenu(PyeMenu):
    """Used for any of the sub menus in a multi-menu instance, e.g. in
       TopMenu(
         MenuItem("Foo", action=SubMenu(
             MenuItem("Bar"),
             MenuItem("Baz"))),
         MenuItem("Quux"))

    Differs from TopMenu in that if you cancel it, it doesn't quit
    but goes back to the previous menu.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("action_handler", SubMenu.action_handler)
        super().__init__(*args, **kwargs)

    def __call__(self, value):
        self.set_position(Gtk.WindowPosition.MOUSE)
        self.show_all()
        return self  # Don't quit

    def action_handler(self, value):
        if isinstance(value, SubMenu):
            self.selected = None
        else:
            if value is not None:
                print(value)
            self.hide()
            if value is not None:  # Not cancelling submenu
                self.destroy()
                Gtk.main_quit()


class SubMenuItem(MenuItem):
    """Wrapper for MenuItem(label, action=SubMenu(items))"""

    def __init__(self, label, *items, **opts):
        super().__init__(label, action=SubMenu(*items, **opts))
