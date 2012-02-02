# -*- coding: utf-8 -*-
# PiTiVi , Non-linear video editor
#
#       transitions.py
#
# Copyright (c) 2012, Jean-François Fortin Tam <nekohayo@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.

# TODO: cleanup ces imports
import gst
import gtk
import os
import gobject
import pango

from gettext import gettext as _
from xml.sax.saxutils import escape

from pitivi.configure import get_pixmap_dir
from pitivi.utils.loggable import Loggable
from pitivi.utils.ui import SPACING

(COL_NAME_TEXT,
 COL_DESC_TEXT,
 COL_TRANSITION_TYPE,
 COL_TRANSITION_ID,
 COL_ICON) = range(5)


class TransitionsListWidget(gtk.VBox, Loggable):
    """
    Widget for listing and selecting transitions
    """

    def __init__(self, instance, uiman):
        gtk.VBox.__init__(self)
        Loggable.__init__(self)

        self.app = instance

        #Tooltip handling
        self._current_transition_name = None
        self._current_tooltip_icon = None

        #Searchbox
#        hsearch = gtk.HBox()
#        hsearch.set_spacing(SPACING)
#        hsearch.set_border_width(3)  # Prevents being flush against the notebook
#        searchStr = gtk.Label(_("Search:"))
#        self.searchEntry = gtk.Entry()
#        self.searchEntry.set_icon_from_stock(gtk.ENTRY_ICON_SECONDARY, "gtk-clear")
#        hsearch.pack_start(searchStr, expand=False)
#        hsearch.pack_end(self.searchEntry, expand=True)

        self.storemodel = gtk.ListStore(str, str, str, str, gtk.gdk.Pixbuf)

        self.iconview_scrollwin = gtk.ScrolledWindow()
        self.iconview_scrollwin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.iconview_scrollwin.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        self.iconview = gtk.IconView(self.storemodel)
        self.iconview.set_pixbuf_column(COL_ICON)
        self.iconview.set_text_column(COL_NAME_TEXT)
        self.iconview.set_item_width(48 + 10)
        self.iconview_scrollwin.add(self.iconview)
        self.iconview.set_property("has_tooltip", True)

#        self.searchEntry.connect("changed", self.searchEntryChangedCb)
#        self.searchEntry.connect("focus-in-event", self.searchEntryActivateCb)
#        self.searchEntry.connect("focus-out-event", self.searchEntryDesactvateCb)
#        self.searchEntry.connect("icon-press", self.searchEntryIconClickedCb)
        self.iconview.connect("button-release-event", self._buttonReleaseCb)
        self.iconview.connect("query-tooltip", self._queryTooltipCb)

        # Speed-up startup by only checking available transitions on idle
        gobject.idle_add(self._loadAvailableTransitionsCb)

#        self.pack_start(hsearch, expand=False)
        self.pack_end(self.iconview_scrollwin, expand=True)

        #create the filterModel
        self.modelFilter = self.storemodel.filter_new()
#        self.modelFilter.set_visible_func(self._setRowVisible, data=None)
        self.iconview.set_model(self.modelFilter)

#        hsearch.show_all()

    def _loadAvailableTransitionsCb(self):
        """
        Get the list of transitions from GES and load the associated thumbnails.
        """
        for transition in ges_transition_enum_items:  # TODO
            self.storemodel.append([transition.value_nick,
                                     transition.value_name,
                                     transitionType,
                                     transition.numerator,
                                     self._getIcon(transition.value_nick)])
            self.storemodel.set_sort_column_id(COL_NAME_TEXT, gtk.SORT_ASCENDING)

    def _buttonReleaseCb(self, view, event):
        if event.button == 1:
            transition_id = self.getSelectedItem()
        return True

    def _queryTooltipCb(self, view, x, y, keyboard_mode, tooltip):
        context = view.get_tooltip_context(x, y, keyboard_mode)
        if context is None:
            return False

        view.set_tooltip_item(tooltip, context[1][0])

        name = self.modelFilter.get_value(context[2], COL_TRANSITION_ID)
        if self._current_transition_name != name:
            self._current_transition_name = name
            icon = self.modelFilter.get_value(context[2], COL_ICON)
            self._current_tooltip_icon = icon

        longname = escape(self.modelFilter.get_value(context[2], COL_NAME_TEXT).strip())
        description = escape(self.modelFilter.get_value(context[2], COL_DESC_TEXT))
        txt = "<b>%s:</b>\n%s" % (longname, description)
        tooltip.set_markup(txt)
        return True

    def getSelectedItem(self):
        path = self.iconview.get_selected_items()
        path = self.modelFilter.convert_path_to_child_path(path[0])
        return self.storemodel[path][COL_TRANSITION_ID]

#    def searchEntryChangedCb(self, entry):
#        self.modelFilter.refilter()

#    def searchEntryIconClickedCb(self, entry, unused, unsed1):
#        entry.set_text("")

#    def searchEntryDesactvateCb(self, entry, event):
#        self.app.gui.setActionsSensitive("default", True)
#        self.app.gui.setActionsSensitive(['DeleteObj'], True)

#    def searchEntryActivateCb(self, entry, event):
#        self.app.gui.setActionsSensitive("default", False)
#        self.app.gui.setActionsSensitive(['DeleteObj'], False)

#    def _setRowVisible(self, model, iter, data):
#        """
#        Filters the icon view depending on the search results
#        """
#        text = self.searchEntry.get_text().lower()
#        return text in model.get_value(iter, COL_DESC_TEXT).lower() or\
#               text in model.get_value(iter, COL_NAME_TEXT).lower()
#        return False
