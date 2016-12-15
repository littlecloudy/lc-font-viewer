#! /env/bin python3

from fontviewer import *



class App (Gtk.Application):
  def __init__ (self):
    Gtk.Application.__init__ (self,
                              application_id='org.littlecloudy.fontviewer',
                              flags=Gio.ApplicationFlags.FLAGS_NONE)

    self.connect ('activate', self.on_activate_app)

  def on_activate_app (self, app):
    win = Gtk.Window ()
    win.set_default_size (400,300)
    app.add_window (win)

    header = Gtk.HeaderBar ()
    header.set_title ('Font Viewer')
    header.set_subtitle ('by Little Cloudy')
    header.set_show_close_button (True)

    back_button = Gtk.Button ('Back')
    header.pack_start (back_button)
    back_button.set_sensitive (False)
    win.set_titlebar (header)
  
    fontviewer = FontViewerApp (back_button)
    win.add (fontviewer)

    win.show_all ()
   
    

if __name__ == '__main__':
  app = App ()
  app.run (None)
