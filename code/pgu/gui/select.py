"""
"""
from const import *
import table
import basic, button

class Select(table.Table):
    """A select input.
    
    <pre>Select(value=None)</pre>
    
    <dl>
    <dt>value<dd>initial value
    </dl>
    
    <strong>Example</strong>
    <code>
    w = Select(value="goats")
    w.add("Cats","cats")
    w.add("Goats","goats")
    w.add("Dogs","Dogs")
    
    w.value = 'dogs' #changes the value from goats to dogs
    </code>
    
    """

    def __init__(self,value=None,**params):
        params.setdefault('cls','select')
        table.Table.__init__(self,**params)
        
        self.top_selected = button.Button(cls=self.cls+".selected")
        table.Table.add(self,self.top_selected) #,hexpand=1,vexpand=1)#,0,0)
        self.top_selected.value = basic.Label(" ",cls=self.cls+".option.label")
        
        self.top_arrow = button.Button(basic.Image(self.style.arrow),cls=self.cls+".arrow")
        table.Table.add(self,self.top_arrow) #,hexpand=1,vexpand=1) #,1,0)
        
        self.options = table.Table() #style={'border':3})
        self.options_first = None
        
        self.options.tr()
        self.spacer_top = basic.Spacer(0,0)
        self.options.add(self.spacer_top)
        
        self.options.tr()
        self._options = table.Table(cls=self.cls+".options")
        self.options.add(self._options)
        
        self.options.tr()
        self.spacer_bottom = basic.Spacer(0,0)
        self.options.add(self.spacer_bottom)

        
        self.options.connect(BLUR,self._close,None)
        self.spacer_top.connect(CLICK,self._close,None)
        self.spacer_bottom.connect(CLICK,self._close,None)
        
        self.values = []
        self.value = value
    
    def resize(self,width=None,height=None):
        max_w,max_h = 0,0
        for w in self._options.widgets:
            w.rect.w,w.rect.h = w.resize()
            max_w,max_h = max(max_w,w.rect.w),max(max_h,w.rect.h)
        
        #xt,xr,xb,xl = self.top_selected.getspacing()
        self.top_selected.style.width = max_w #+ xl + xr
        self.top_selected.style.height = max_h #+ xt + xb
        
        self.top_arrow.connect(CLICK,self._open,None)
        self.top_selected.connect(CLICK,self._open,None)
        
        w,h = table.Table.resize(self,width,height)
        
        self.spacer_top.style.width, self.spacer_top.style.height = w,h
        self.spacer_bottom.style.width, self.spacer_bottom.style.height = w,h
        self._options.style.width = w
        #HACK: sort of, but not a big one..
        self._options.resize()
        
        return w,h
        
    def _open(self,value):
        sh = self.rect.h #spacer height
        opts = self.options
        
        self.spacer_top.style.height = 0
        self.spacer_bottom.style.height = 0
        opts.rect.w, opts.rect.h = opts.resize()
        h = opts.rect.h
        
        y = self.rect.y
        c = self.container
        while hasattr(c,'container'):
            y += c.rect.y
            if c.container == None: break
            c = c.container
            
        if y + sh + h <= c.rect.h: #down
            self.spacer_top.style.height = sh
            dy = self.rect.y
        else: #up
            self.spacer_bottom.style.height = sh
            dy = self.rect.y - h
            
        opts.rect.w, opts.rect.h = opts.resize()
            
        self.container.open(opts,self.rect.x,dy)
        self.options_first.focus()
        
    def _close(self,value):
#         print 'my close!'
        self.options.close()
        self.top_selected.focus()
#         self.blur()
#         self.focus()
#         print self.container.myfocus == self
    
    def _setvalue(self,value):
        self.value = value._value
        if hasattr(self,'container'):
            #self.chsize()
            #HACK: improper use of resize()
            #self.resize() #to recenter the new value, etc.
            pass
        #    #self._resize()
        
        self._close(None)
        #self.repaint() #this will happen anyways
        
    
    
    def __setattr__(self,k,v):
        mywidget = None
        if k == 'value':
            for w in self.values:
                if w._value == v:
                    mywidget = w
        _v = self.__dict__.get(k,NOATTR)
        self.__dict__[k]=v
        if k == 'value' and _v != NOATTR and _v != v: 
            self.send(CHANGE)
            self.repaint()
        if k == 'value':
            if not mywidget:
                mywidget = basic.Label(" ",cls=self.cls+".option.label")
            self.top_selected.value = mywidget
    
    def add(self,w,value=None):
        """Add a widget, value item to the Select.
        
        <pre>Select.add(widget,value=None)</pre>
        
        <dl>
        <dt>widget<dd>Widget or string to represent the item
        <dt>value<dd>value for this item
        </dl>
        
        <strong>Example</strong>
        <code>
        w = Select()
        w.add("Goat") #adds a Label
        w.add("Goat","goat") #adds a Label with the value goat
        w.add(gui.Label("Cuzco"),"goat") #adds a Label with value goat
        </code>
        """
        
        if type(w) == str: w = basic.Label(w,cls=self.cls+".option.label")
        
        w.style.align = -1
        b = button.Button(w,cls=self.cls+".option")
        b.connect(CLICK,self._setvalue,w)
        #b = w
        #w.cls = self.cls+".option"
        #w.cls = self.cls+".option"
        
        self._options.tr()
        self._options.add(b) #,align=-1)
        
        if self.options_first == None:
            self.options_first = b
        #self._options.td(b, align=-1, cls=self.cls+".option")
        #self._options.td(_List_Item(w,value=value),align=-1)
        
        if value != None: w._value = value
        else: w._value = w
        if self.value == w._value:
            self.top_selected.value = w
        self.values.append(w)
