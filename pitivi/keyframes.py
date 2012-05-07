import gtk
import os
import goocanvas
import ges
import cairo

from pitivi.configure import get_ui_dir
from pitivi.timeline.track import TrackFileSource
from pitivi.utils.timeline import Zoomable
from pitivi.utils.ui import unpack_cairo_gradient
from pitivi.timeline.curve import Curve


class DummyTrackSource(goocanvas.Group):
    def __init__(self, instance, element, interp, name):
        goocanvas.Group.__init__(self)
        self.bg = goocanvas.Rect(height=100, line_width=1)
        self.set_simple_transform(0, 0, 1, 0)
        color = 0x00facc2e
        pattern = unpack_cairo_gradient(color)
        self.bg.props.width = 600
        self.bg.props.height = 100
        self.bg.props.fill_pattern = pattern
        self.add_child(self.bg)
        curve = Curve(instance, element, interp, name)
        self.add_child(curve)


class KeyframeDisplay(goocanvas.Canvas, Zoomable):
    def __init__(self, timeline_object, instance, effect, name):
        goocanvas.Canvas.__init__(self)
        Zoomable.__init__(self)
        self.controller = ges.Controller()
        self.controller.set_controlled(effect)
        self.app = None
        self.get_root_item().set_simple_transform(0, 2.0, 1.0, 0)
        self.set_bounds(0, 0, 600, 600)
        for elem in timeline_object.get_track_objects():
            if isinstance(elem, ges.TrackSource):
                break
        w = DummyTrackSource(instance, effect, self.controller, name)
        self.get_root_item().add_child(w)


class KeyframeEditor():
    def __init__(self, element, tl_object, instance):
        self.element = element
        self.instance = instance
        self.tl_object = tl_object
        print tl_object
        self._createUI()
        self.dialog.run()

    def _createUI(self):
        name = None
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(get_ui_dir(), "keyframes.ui"))

        self.dialog = builder.get_object("dialog1")
        self.storemodel = builder.get_object("liststore1")
        box = builder.get_object("box1")

        self.dialog.set_default_size(800, 600)
        for prop in self.element.list_children_properties():
            if not name:
                name = prop.name
            self.storemodel.append([prop.name])
            #self._current_element_values[prop.name] = element.get_child_property(prop.name)
        display = KeyframeDisplay(self.tl_object, self.instance, self.element, name)
        box.pack_start(display, expand=True)
        display.show()
