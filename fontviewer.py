#! /env/bin python3

from gi.repository import Gtk,Pango, Gio
from GtkLc import *
import time, threading


lorem_ipsum = "Nemo enim ipsam voluptatem quia voluptas \nsit aspernatur aut odit aut fugit"
abc_preview = "AaBbCcDdEe"

class FontLoader ():
  def __init__ (self):
    widget  = Gtk.Window ()
    self.context = widget.create_pango_context ()
    widget.destroy () # we just need shotcut context
    
    self.fontdict = {}
    self.valist = []
    
  def get_all_fonts (self):
    families = self.context.list_families ()
    for family in families:
      key = family.get_name()
      for face in family.list_faces ():
        value = face.get_face_name()
        self.valist.append (value)
      self.fontdict [key] = self.valist
      self.valist = []
    # return dict, key=family and value=faces list
    return self.fontdict

  def get_font_face_from_family (self, family):
    # return list of font faces
    return self.fontdict [family]

  def get_count_family (self):
    return len (self.fontdict)

# faux widget
class ListBoxFontWidget (Gtk.Grid):
  # index ?, font family string, list of faces, len face int
  def __init__ (self, index, family, face, lenface):
    self.family = family
    self.face   = face

    Gtk.Grid.__init__ (self)
    GtkLc.set_all_margins_widget (self, 10)
    
    fontdesc = Pango.FontDescription.from_string (family + ' Regular ' + '16')
    
    preview_label = Gtk.Label (abc_preview)
    preview_label.set_halign (Gtk.Align.START)
    preview_label.override_font (fontdesc)
    self.attach (preview_label, 0,0,1,1)

    bottomGrid = Gtk.Grid ()
    bottomGrid.set_hexpand (True)
    bottomGrid.set_row_homogeneous (True)
    self.attach (bottomGrid, 0,1,1,1)

    family_label = Gtk.Label (family)
    bottomGrid.attach (family_label, 0,0,1,1)

    face_label = Gtk.Label (str(lenface) + " fonts")
    face_label.set_hexpand (True)
    face_label.set_halign (Gtk.Align.END)
    bottomGrid.attach (face_label, 1,0,1,1)


class FontViewerAppSplash (Gtk.Grid):
  def __init__ (self):
    Gtk.Grid.__init__ (self)
 
    preview_label = Gtk.Label ('Current system font')
    self.attach (preview_label, 0,0,1,1)

    preview_text = Gtk.Label (lorem_ipsum)
    self.attach (preview_text, 0,1,1,1)

    


class FontViewerApp (Gtk.Stack):
  def __init__ (self, navi_button):
    Gtk.Stack.__init__ (self)
    self.set_name ('MainGrid')
    cssprov = Gtk.CssProvider()
    css = b"""#MainGrid {
                 background-color : white;
              }
           """
    cssprov.load_from_data (css)
    stylecontext = self.get_style_context ()
    stylecontext.add_provider_for_screen (Gdk.Screen.get_default (),cssprov, 600) 

    mainGrid = Gtk.Grid ()
    self.add_named (mainGrid, 'mainGrid')

    mainBar = Gtk.Toolbar ()
    mainBar.set_hexpand (True)
    mainGrid.attach (mainBar, 0,0,1,1)
    
    levelBar = Gtk.ProgressBar ()
    mainGrid.attach (levelBar, 0,1,1,1)

    scrWin = Gtk.ScrolledWindow () 
    scrWin.set_vexpand (True)
    mainGrid.attach (scrWin, 0,2,1,1)

    
    # peak at around 46 MB----------------------nice interface
    # long process block ui, stable

    flowBox = Gtk.FlowBox ()
    flowBox.set_property ('activate-on-single-click', False)
    flowBox.set_column_spacing  (15)
    flowBox.set_homogeneous (True)
    GtkLc.set_all_margins_widget (flowBox, 15)
    scrWin.add (flowBox)

    statusBar = Gtk.Label ()
    statusBar.set_valign (Gtk.Align.END)
    mainGrid.attach (statusBar, 0,3,1,1)

    statusBuffer = 0
    floader = FontLoader ()
    
    fontdict = floader.get_all_fonts ()
    for family,face in fontdict.items ():
      widget = ListBoxFontWidget (0, family, face, len(face))
      flowBox.add (widget)
      flowBox.show_all () 

    detGrid = Gtk.Grid ()
    self.add_named (detGrid, 'detGrid')

    detScr = Gtk.ScrolledWindow ()
    detScr.set_hexpand (True)
    detScr.set_vexpand (True)
    detGrid.attach (detScr, 0,0,1,1)

    detLabel = Gtk.Label ()
    detLabel.set_single_line_mode (False)
    detScr.add (detLabel)

    detBar = GtkLc.Sidebar ()
    detGrid.attach (detBar, 1,0,1,1)

    detTview = Gtk.TreeView ()
    scrTview = Gtk.ScrolledWindow ()
    scrTview.set_vexpand (True)
    detBar.add_child (scrTview, 0,0,1,1)
    scrTview.add (detTview)

    detModel = Gtk.ListStore (str)
    detTview.set_model (detModel)

    rend = Gtk.CellRendererText ()
    column = Gtk.TreeViewColumn ('Available variants', rend, text=0)
    detTview.append_column (column)

    zoom_slider = Gtk.Scale.new_with_range (Gtk.Orientation.HORIZONTAL,6,72,1)
    zoom_slider.set_value (12)
    detBar.add_child (zoom_slider, 0,1,1,1)

    preview_entry = Gtk.Entry ()
    preview_entry.set_placeholder_text ('Type your text here')
    detBar.add_child (preview_entry, 0,2,1,1)
    
    

    self.set_visible_child (mainGrid)


    flowBox.connect       ('child-activated', self.on_activate_detail, detGrid, detLabel, detModel, navi_button)
    zoom_slider.connect   ('value-changed', self.on_move_slider, detLabel)
    detTview.connect      ('row-activated', self.on_row_activated, detLabel)
    preview_entry.connect ('changed', self.on_change_text, detLabel)
    navi_button.connect   ('clicked', self.on_click_navi_button, mainGrid, preview_entry, zoom_slider)

  def on_click_navi_button (self, button, mainGrid, preview_entry, zoom_slider):
    self.set_visible_child (mainGrid)
    button.set_sensitive (False)
    preview_entry.set_text ('')
    zoom_slider.set_value (12)

  def on_activate_detail (self, flowBox, child, detGrid, detLabel, model, navi_button):
    navi_button.set_sensitive (True)
    self.set_visible_child (detGrid)
    detLabel.set_label (lorem_ipsum)
    model.clear ()

    for item in child:
      detLabel.override_font (Pango.FontDescription.from_string (item.family + ' 12 '))
      for face in item.face:
        model.append ([face])

  def on_row_activated (self, tview, path, col, detLabel):
    selection = tview.get_selection ()
    model, viter = selection.get_selected ()
    if viter is not None:
      variant = model [viter] [0]
      detLabel.override_font (Pango.FontDescription.from_string (variant))

  def on_move_slider (self, slider, label):
    value = slider.get_value ()
    label.override_font (Pango.FontDescription.from_string (str(value)))  
    
  def on_change_text (self, entry, label):
    cur_txt = entry.get_text ()
    if cur_txt == '':
      label.set_text (lorem_ipsum)   
    else:
      label.set_text (entry.get_text ())

  # choices of data view

    # peaked at around 45 MB ------------------------ very simple list
    # fix the renderer
    #tview = Gtk.TreeView ()
    #scrWin.add (tview)

    #model = Gtk.ListStore (str, int)
    #tview.set_model (model)

    #rend = Gtk.CellRendererText ()
    #column_name = Gtk.TreeViewColumn ('', rend, text=0)
    #tview.append_column (column_name)
    #column_len = Gtk.TreeViewColumn ('', rend, text=1)
    #tview.append_column (column_len)

    #floader = FontLoader ()
    #self.update_view (model, rend, floader)

  #def update_view (self, model, rend, floader):
    #model.clear ()
    #fontdict = floader.get_all_fonts ()
    #for family,face in fontdict.items ():
      #rend.set_property ('font-desc', Pango.FontDescription.from_string (family + ' Regular ' + '16'))
      #model.append ([family, len(face) ])
    #-------------------------------------------------------------------  
  
  
    # peaked at 48 MB around------------------- nice interface, crashing 
    # due to threading

    #flowBox = Gtk.FlowBox ()
    #flowBox.set_column_spacing  (15)
    #flowBox.set_homogeneous (True)
    #GtkLc.set_all_margins_widget (flowBox, 15)
    #scrWin.add (flowBox)

    #statusBar = Gtk.Label ()
    #statusBar.set_halign (Gtk.Align.END)
    #statusBar.set_valign (Gtk.Align.END)
    #self.attach (statusBar, 0,3,1,1)

    #statusBuffer = 0
    #floader = FontLoader ()

    #self.thread = threading.Thread (target=self.update_data, args=(floader,levelBar,flowBox, statusBar, statusBuffer))
    #self.thread.daemon = True
    #self.thread.start ()

  #def update_data (self, floader, levelBar, flowBox, statusBar, statusBuffer):
    #fontdict = floader.get_all_fonts ()
    #for family,face in fontdict.items ():
      #widget = ListBoxFontWidget (0, family, len(face))
      #flowBox.add (widget)
      #widget.show_all ()
      #statusBuffer += 1

      #GLib.idle_add (self.update_view, levelBar, flowBox, widget, statusBar, statusBuffer, len(fontdict))
      #time.sleep (0.1)

  #def update_view (self, levelBar, flowBox, widget, statusBar, statusBuffer, len_family):
      #levelBar.pulse ()
      
      #statusBar.set_label (str(statusBuffer))
      #if statusBuffer == len_family:
        #levelBar.set_fraction (1.0)
        #return True
      
      #return False
    #-------------------------------------------------------------------
    
    
    
  
