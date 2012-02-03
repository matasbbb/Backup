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
import ges
import gtk
import os
import gobject
import pango

from gettext import gettext as _
from xml.sax.saxutils import escape

from pitivi.configure import get_pixmap_dir
from pitivi.utils.loggable import Loggable
from pitivi.utils.ui import SPACING, PADDING

(COL_TRANSITION_ID,
 COL_NAME_TEXT,
 COL_DESC_TEXT,
 COL_ICON) = range(4)


class TransitionsListWidget(gtk.VBox, Loggable):
    """
    Widget for listing and selecting transitions
    """

    def __init__(self, instance, uiman):
        gtk.VBox.__init__(self)
        Loggable.__init__(self)

        self.app = instance
        self._pixdir = os.path.join(get_pixmap_dir(), "transitions")
        icon_theme = gtk.icon_theme_get_default()
        self._question_icon = icon_theme.load_icon("dialog-question", 48, 0)

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

        self.infobar = gtk.InfoBar()
        txtlabel = gtk.Label()
        txtlabel.set_padding(PADDING, PADDING)
        txtlabel.set_line_wrap(True)
        txtlabel.set_line_wrap_mode(pango.WRAP_WORD)
        txtlabel.set_justify(gtk.JUSTIFY_CENTER)
        txtlabel.set_text(
            _("Create a transition by overlapping two adjacent clips on the "
                "same layer. Click the transition on the timeline to change "
                "the transition type."))
        self.infobar.add(txtlabel)
        self.infobar.show_all()

        self.storemodel = gtk.ListStore(str, str, str, gtk.gdk.Pixbuf)

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
        self.pack_start(self.infobar, expand=False)
        self.pack_end(self.iconview_scrollwin, expand=True)

        #create the filterModel
        self.modelFilter = self.storemodel.filter_new()
#        self.modelFilter.set_visible_func(self._setRowVisible, data=None)
        self.iconview.set_model(self.modelFilter)
        self.iconview_scrollwin.show_all()
#        hsearch.show_all()

        self.deactivate()

    def _loadAvailableTransitionsCb(self):
        """
        Get the list of transitions from GES and load the associated thumbnails.
        """
        # TODO: rewrite this method when GESRegistry exists
        self.available_transitions = []
        # GES currently has transitions IDs up to 512
        # Number 0 means "no transition", so we might just as well skip it.
        for i in range(1, 513):
            try:
                transition = ges.VideoStandardTransitionType(i)
            except ValueError:
                # We hit a gap in the enum
                pass
            else:
                self.available_transitions.append(\
                    [transition.numerator,
                    transition.value_nick,
                    transition.value_name])
                self.storemodel.append(\
                    [transition.numerator,
                    transition.value_nick,
                    transition.value_name,
                    self._getIcon(transition.value_nick)])

#            self.storemodel.set_sort_column_id(COL_NAME_TEXT, gtk.SORT_ASCENDING)

    def activate(self, transition):
        """
        Hide the infobar and make the transitions UI sensitive.
        """
        self.app.gui.switchContextTab("transitions")
        self.iconview.set_sensitive(True)
        self.infobar.hide()
        model = self.iconview.get_model()
        for row in model:
            if int(transition.numerator) == int(row[COL_TRANSITION_ID]):
                self.iconview.select_path(model.get_path(row.iter))

    def deactivate(self):
        """
        Show the infobar and make the transitions UI insensitive.
        """
        self.iconview.unselect_all()
        self.iconview.set_sensitive(False)
        self.infobar.show()

    def _getIcon(self, transition_nick):
        """
        If available, return an icon pixbuf for a given transition nickname.
        """
        name = transition_nick + ".png"
        icon = None
        try:
            icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self._pixdir, name))
        except:
            try:
                icon = self._question_icon
            except:
                icon = None
        return icon

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
