#!/usr/bin/env python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import pygtk
pygtk.require("2.0")
import gtk
import os
import shutil
import gobject
import gettext
import gnomevfs
from gnome import ui
from UserDir import UserdirFile
from common.Constants import *
from common.Widgets import TweakPage, WarningDialog, DirView, FlatView

(
    COLUMN_ICON,
    COLUMN_TEMPINFO,
    COLUMN_FILE,
) = range(3)

class AbstractTempates:
    systemdir = os.path.join(os.path.expanduser("~"), ".ubuntu-tweak/templates")
    userdir = os.getenv("HOME") + "/"  + "/".join([dir for dir in UserdirFile().get('XDG_TEMPLATES_DIR').strip('"').split("/")[1:]])

class DefaultTemplates(AbstractTempates):
    """This class use to create the default templates"""
    templates = {
            "HTML document.html": _("HTML document"),
            "ODB Database.odb": _("ODB Database"),
            "ODS Spreadsheet.ods": _("ODS Spreadsheet"),
            "ODT Document.odt": _("ODT Document"),
            "Plain text document.txt": _("Plain text document"),
            "ODP Presentation.odp": _("ODP Presentation"),
            "Python script.py": _("Python script"),
            "Shell script.sh": _("Shell script")
            }

    def create(self):
        if not os.path.exists(self.systemdir):
            os.makedirs(self.systemdir)
        for file, des in self.templates.items():
            realname = "%s.%s" % (des, file.split('.')[1])
            if not os.path.exists(os.path.join(self.systemdir, realname)):
                shutil.copy(os.path.join(DATA_DIR, 'templates/%s' % file), os.path.join(self.systemdir, realname))

    def remove(self):
        if not os.path.exists(self.systemdir):
            return 
        if os.path.isdir(self.systemdir): 
            for root, dirs, files in os.walk(self.systemdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    os.rmdir(self.systemdir)
        else:
            os.unlink(self.systemdir)
        return

class EnableTemplate(DirView, AbstractTempates):
    """The treeview to display the enable templates"""
    type = _("Enabled Templates")

    def __init__(self):
        DirView.__init__(self, self.userdir)

class DisableTemplate(FlatView, AbstractTempates):
    """The treeview to display the system template"""
    type = _("Disabled Templates")

    def __init__(self):
        FlatView.__init__(self, self.systemdir, self.userdir)

class Templates(TweakPage, AbstractTempates):
    """Freedom added your docmuent templates"""
    def __init__(self):
        TweakPage.__init__(self, 
                _("Manage your templates"),
                _('You can freely manage your document templates.\nYou can drag and drop from File Manager.\n"Create Document" will be added to the Context Menu.\n'))

        self.default = DefaultTemplates()
        self.config_test()

        hbox = gtk.HBox(False, 10)
        self.pack_start(hbox)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.enable_templates = EnableTemplate()
        sw.add(self.enable_templates)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.disable_templates = DisableTemplate()
        sw.add(self.disable_templates)

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, False, False, 10)

        button = gtk.Button(_("Rebuild the system templates"))
        button.connect("clicked", self.on_rebuild_clicked)
        hbox.pack_end(button, False, False, 5)

        self.enable_templates.connect('drag_data_received', self.on_enable_drag_data_received)
        self.enable_templates.connect('deleted', self.on_enable_deleted)
        self.disable_templates.connect('drag_data_received', self.on_disable_drag_data_received)

    def on_enable_deleted(self, widget):
        self.disable_templates.update_model()

    def on_enable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.disable_templates.update_model()

    def on_disable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.enable_templates.update_model()

    def on_rebuild_clicked(self, widget):
        dialog = WarningDialog(_("This will delete all the disabled templates, continue?"))
        if dialog.run() == gtk.RESPONSE_YES:
            self.default.remove()
            self.default.create()
            self.disable_templates.update_model()
        dialog.destroy()

    def config_test(self):
        if not os.path.exists(self.systemdir):
            self.default.create()

if __name__ == "__main__":
    from Utility import Test
    Test(Templates)