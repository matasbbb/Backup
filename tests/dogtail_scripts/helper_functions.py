#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import re
from dogtail.predicate import GenericPredicate
from test_base import BaseDogTail
import dogtail.rawinput
from time import sleep
from pyatspi import Registry as registry
from pyatspi import (KEY_SYM, KEY_PRESS, KEY_PRESSRELEASE, KEY_RELEASE)


class HelpFunc(BaseDogTail):

    def saveProject(self, path=None, saveAs=True):
        proj_menu = self.menubar.menu("Project")
        proj_menu.click()
        if saveAs:
            self.assertIsNotNone(path)
            proj_menu.menuItem("Save As...").click()
            save_dialog = self.pitivi.child(name="Save As...", roleName='dialog', recursive=False)
            # In GTK3's file chooser, you can enter /tmp/foo.xptv directly
            # In GTK2 however, you must do it in two steps:
            path_dir, filename = os.path.split(path)
            text_field = save_dialog.child(roleName="text")
            text_field.text = path_dir
            dogtail.rawinput.pressKey("Enter")
            sleep(0.05)
            text_field.text = filename
            dogtail.rawinput.pressKey("Enter")
            # Save to the list of items to cleanup afterwards
            self.unlink.append(path)
        else:
            # Just save
            proj_menu.menuItem("Save").click()

    def loadProject(self, url, expect_unsaved_changes=False):
        proj_menu = self.menubar.menu("Project")
        proj_menu.click()
        proj_menu.menuItem("Open...").click()
        load = self.pitivi.child(roleName='dialog', recursive=False)
        load.child(name="Type a file name", roleName="toggle button").click()
        load.child(roleName='text').text = url
        load.button('Open').click()
        # If an unsaved changes confirmation dialog shows up, deal with it
        if expect_unsaved_changes:
            # Simply try searching for the existence of the dialog's widgets
            # If it fails, dogtail will fail with a SearchError, which is fine
            self.pitivi.child(name="Close without saving", roleName="push button").click()

    def search_by_text(self, text, parent, name=None, roleName=None):
        """
        Search a parent widget for childs containing the given text
        """
        children = parent.findChildren(GenericPredicate(roleName=roleName, name=name))
        for child in children:
            if child.text == text:
                return child

    def search_by_regex(self, regex, parent, name=None, roleName=None, regex_flags=0):
        """
        Search a parent widget for childs containing the given regular expression
        """
        children = parent.findChildren(GenericPredicate(roleName=roleName, name=name))
        r = re.compile(regex, regex_flags)
        for child in children:
            if child.text is not None and r.match(child.text):
                return child

    def insert_clip(self, icon, n=1):
        icon.select()
        lib = self.menubar.menu("Library")
        insert = lib.child("Insert at End of Timeline")
        for i in range(n):
            sleep(0.3)
            lib.click()
            sleep(0.1)
            insert.click()
        icon.deselect()

    def import_media(self, filename="1sec_simpsons_trailer.mp4"):
        dogtail.rawinput.pressKey("Esc")  # Ensure the welcome dialog is closed
        # Use the menus, as the main toolbar might be hidden
        lib_menu = self.menubar.menu("Library")
        lib_menu.click()
        import_menu_item = lib_menu.child("Import Files...")
        import_menu_item.click()

        # Force dogtail to look only one level deep, which is much faster
        # as it doesn't have to analyze the whole mainwindow.
        import_dialog = self.pitivi.child(name="Select One or More Files",
                                          roleName="dialog", recursive=False)
        # Instead of checking for the presence of the path text field and then
        # searching for the toggle button to enable it, use the fact that GTK's
        # file chooser allows typing the path directly if it starts with "/".
        dogtail.rawinput.pressKey("/")  # This text will be replaced later

        filepath = os.path.realpath(__file__).split("dogtail_scripts/")[0]
        filepath += "samples/" + filename
        import_dialog.child(roleName='text').text = filepath
        dogtail.rawinput.pressKey("Enter")  # Don't search for the Add button
        sleep(0.6)

        # Check if the item is now visible in the media library.
        libtab = self.pitivi.tab("Media Library")
        for i in range(5):
            # The time it takes for the icon to appear is unpredictable,
            # therefore we try up to 5 times to look for it
            icons = libtab.findChildren(GenericPredicate(roleName="icon"))
            for icon in icons:
                if icon.text == filename:
                    return icon
            sleep(0.5)
        # Failure to find an icon might be because it is hidden due to a search
        current_search_text = libtab.child(roleName="text").text.lower()
        self.assertNotEqual(current_search_text, "")
        self.assertNotIn(filename.lower(), current_search_text)
        return None

    def import_media_multiple(self, files):
        dogtail.rawinput.pressKey("Esc")  # Ensure the welcome dialog is closed
        # Use the menus, as the main toolbar might be hidden
        lib_menu = self.menubar.menu("Library")
        lib_menu.click()
        import_menu_item = lib_menu.child("Import Files...")
        import_menu_item.click()

        # Same performance hack as in the import_media method
        import_dialog = self.pitivi.child(name="Select One or More Files",
                                          roleName="dialog", recursive=False)
        dogtail.rawinput.pressKey("/")
        dir_path = os.path.realpath(__file__).split("dogtail_scripts/")[0] + "samples/"
        import_dialog.child(roleName='text').text = dir_path
        dogtail.rawinput.pressKey("Enter")

        # We are now in the samples directory, select various items.
        # We use Ctrl click to select multiple items. However, since the first
        # row of the filechooser is always selected by default, we must not use
        # ctrl when selecting the first item of our list, in order to deselect.
        ctrl_code = dogtail.rawinput.keyNameToKeyCode("Control_L")
        file_list = import_dialog.child(name="Files", roleName="table")
        first = True
        for f in files:
            sleep(0.5)
            file_list.child(name=f).click()
            if first:
                registry.generateKeyboardEvent(ctrl_code, None, KEY_PRESS)
                first = False
        registry.generateKeyboardEvent(ctrl_code, None, KEY_RELEASE)
        import_dialog.button('Add').click()

        libtab = self.pitivi.tab("Media Library")
        current_search_text = libtab.child(roleName="text").text.lower()
        if current_search_text != "":
            # Failure to find some icons might be because of search filtering.
            # The following avoids searching for files that can't be found.
            for f in files:
                if current_search_text not in f.lower():
                    files.remove(f)
        # Check if non-filtered items are now visible in the media library.
        samples = []
        for i in range(5):
            # The time it takes for icons to appear is unpredictable,
            # therefore we try up to 5 times to look for them
            icons = libtab.findChildren(GenericPredicate(roleName="icon"))
            for icon in icons:
                for f in files:
                    if icon.text == f:
                        samples.append(icon)
                        files.remove(f)
            if len(files) == 0:
                break
            sleep(0.5)
        return samples

    def get_timeline(self):
        # TODO: find a better way to identify
        return self.pitivi.children[0].children[0].children[2].children[1].children[3]

    def improved_drag(self, from_coords, to_coords, middle=[], absolute=True, moveAround=True):
        """
        Allow dragging from a set of coordinates to another set of coords,
        with an optional list of intermediate coordinates and the ability to
        wiggle the mouse slightly at each set of coordinates.
        """
        # Choose the default type of motion calculation
        if absolute:
            fun = dogtail.rawinput.absoluteMotion
        else:
            fun = dogtail.rawinput.relativeMotion

        # Do the initial click
        dogtail.rawinput.press(from_coords[0], from_coords[1])
        if moveAround:
            dogtail.rawinput.relativeMotion(5, 5)
            dogtail.rawinput.relativeMotion(-5, -5)

        # Do all the intermediate move operations
        for mid in middle:
            fun(mid[0], mid[1])
            if moveAround:
                dogtail.rawinput.relativeMotion(5, 5)
                dogtail.rawinput.relativeMotion(-5, -5)

        # Move to the final coordinates
        dogtail.rawinput.absoluteMotion(to_coords[0], to_coords[1])
        if moveAround:
            dogtail.rawinput.relativeMotion(5, 5)
            dogtail.rawinput.relativeMotion(-5, -5)

        # Release the mouse button
        dogtail.rawinput.release(to_coords[0], to_coords[1])
