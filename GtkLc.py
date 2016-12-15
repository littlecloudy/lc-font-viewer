#! /env/bin python3

from gi.repository import Gtk,Gdk,GLib
import cairo, math

class GtkLc ():
  def __init__ (self):
    pass

  def set_all_margins_widget (widget, size):
    widget.set_margin_top    (size)
    widget.set_margin_bottom (size)
    widget.set_margin_left   (size)
    widget.set_margin_right  (size)
    
  # faux class
  class Sidebar (Gtk.Grid):
    def __init__ (self):
      Gtk.Grid.__init__ (self)
      Gtk.StyleContext.add_class (self.get_style_context(), 'sidebar')

    def add_child (self, widget, left, top, width, height):
      self.attach (widget, left, top, width, height)

 
  class CircularLevelBar (Gtk.Container):
    __gtype_name__ = 'GtkLcCircularLevelBar'
  
    def __init__(self, *args, **kwds):
      super().__init__(*args, **kwds)
      self.set_size_request(200, 200)
      self.max_value  = 1.0
      self.circ_value = 1.0
    
    # super
    def do_draw(self, cr):
      self.update_angle ()
   
      bg_color = self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
      cr.set_source_rgba(*list(bg_color))
      cr.paint()
        
      allocation = self.get_allocation()
      fg_color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
      
      cr.set_source_rgba(0.1,0.1,0.1,0.2);
      cr.set_line_width(1)
      cr.arc (allocation.width /2 ,
              allocation.height/2 , 
              allocation.height/3 , 
              math.radians (0)    , 
              math.radians (360) )
      cr.stroke()
      
      rgba = Gdk.RGBA ()
      
      ratio = (self.circ_value / self.max_value ) * 100
      #print (ratio)
      if ratio > 45:
        rgba.parse ('#3789FF')
      if ratio < 45 and ratio > 25:
        rgba.parse ('#08D540')
      if ratio < 25:
        rgba.parse ('#FF0000')
      
      cr.set_source_rgba(*list(rgba));
      cr.set_line_width(3)
  
      zero_point = math.radians (-90)
  
      if self.circ_value <= 0:
        self.circ_value = 0
      else:
            
            cr.arc (allocation.width /2 ,
                allocation.height/2 , 
                allocation.height/3 , 
                math.radians (-90)  , # starting point middle top circle
                                      # 0,0 user space starts from right middle
                (zero_point + math.radians (self.angle) ) # end angle: following zero point not user space. user space will end up on 360 deg (right circle)
                )
          
            cr.stroke()
        
   
    # super
    def do_realize(self):
      allocation       = self.get_allocation()
      attr             = Gdk.WindowAttr()
      attr.window_type = Gdk.WindowType.CHILD
      attr.x           = allocation.x
      attr.y           = allocation.y
      attr.width       = allocation.width
      attr.height      = allocation.height
      attr.visual      = self.get_visual()
      attr.event_mask  = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
      WAT              = Gdk.WindowAttributesType
      mask             = WAT.X | WAT.Y | WAT.VISUAL
      window           = Gdk.Window(self.get_parent_window(), attr, mask);
      self.set_window(window)
      self.register_window(window)
      self.set_realized(True)
      window.set_background_pattern(None)      
  
    def update_angle (self):
      if self.circ_value == 0:
        self.max_value   = 1.0
        self.angle       = 1
        return False
      else:
        self.angle       = (self.circ_value/self.max_value) * 360
        return True
  
    def set_value (self, value):
      self.circ_value = float(value)
      self.queue_draw ()
  
    def set_max_value (self, value):
      self.max_value = float(value) 
      self.queue_draw ()
  
    def get_value (self):
      return float (self.circ_value)
  
    def get_max_value (self):
      return float (self.max_value)



    
