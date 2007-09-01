"""
"""
import pygame
from pygame.locals import *

import container
from const import *

class App(container.Container):
    """The top-level widget for an application.
    
    <pre>App(theme=None)</pre>
    
    <dl>
    <dt>theme<dd>an instance of a Theme, optional as it will use the default Theme class.
    </dl>
    
    <strong>Basic Example</strong>
    <code>
    app = gui.App()
    app.run(widget=widget,screen=screen)
    </code>
    
    <strong>Integrated Example</strong>
    <code>
    app = gui.App()
    gui.init(widget=widget)
    while 1:
        for e in pygame.event.get():
            app.event(e)
        app.update(screen)
    </code>
        
    
    
    """
    def __init__(self,theme=None,**params):
        App.app = self
        
        if theme == None: 
            from theme import Theme
            theme = Theme()
        self.theme = theme
        
        params['decorate'] = 'app'
        container.Container.__init__(self,**params)
        self._quit = False
        self.widget = None
        self._chsize = False
        self._repaint = False
        
        self.screen = None
        self.container = None
        self.events = []
        
    def resize(self):
            
        screen = self.screen
        w = self.widget
        wsize = 0
        
        #5 cases
        
        #input screen is already set use its size
        if screen:
            self.screen = screen
            width,height = screen.get_width(),screen.get_height()
        
        #display.screen
        elif pygame.display.get_surface():
            screen = pygame.display.get_surface()
            self.screen = screen
            width,height = screen.get_width(),screen.get_height()
        
        #app has width,height
        elif self.style.width != 0 and self.style.height != 0:
            screen = pygame.display.set_mode((self.style.width,self.style.height),SWSURFACE)
            self.screen = screen
            width,height = screen.get_width(),screen.get_height()
        
        #widget has width,height, or its own size..
        else:
            wsize = 1
            width,height = w.rect.w,w.rect.h = w.resize()
            #w._resize()
            screen = pygame.display.set_mode((width,height),SWSURFACE)
            self.screen = screen
        
        #use screen to set up size of this widget
        self.style.width,self.style.height = width,height
        self.rect.w,self.rect.h = width,height
        self.rect.x,self.rect.y = 0,0
        
        w.rect.x,w.rect.y = 0,0
        w.rect.w,w.rect.h = w.resize(width,height)
        
        for w in self.windows:
            w.rect.w,w.rect.h = w.resize()
            
        self._chsize = False

    
    def init(self,widget=None,screen=None): #TODO widget= could conflict with module widget
        """Initialize the application.
        
        <pre>App.init(widget=None,screen=None)</pre>
        
        <dl>
        <dt>widget<dd>main widget
        <dt>screen<dd>pygame.Surface to render to
        </dl>
        """
        
        App.app = self
        
        if widget: self.widget = widget
        if screen: self.screen = screen
        
        self.resize()   
        
        w = self.widget     
        
        self.widgets = []
        self.widgets.append(w)
        w.container = self
        self.focus(w)
        
        pygame.key.set_repeat(500,30)
        
        self._repaint = True
        self._quit = False
        
        self.send(INIT)
    
    def event(self,e):
        """Pass an event to the main widget.
        
        <pre>App.event(e)</pre>
        
        <dl>
        <dt>e<dd>event
        </dl>
        """
        App.app = self
        #NOTE: might want to deal with ACTIVEEVENT in the future.
        self.send(e.type,e)
        container.Container.event(self,e)
        if e.type == MOUSEBUTTONUP:
            if e.button not in (4,5): #ignore mouse wheel
                sub = pygame.event.Event(CLICK,{
                    'button':e.button,
                    'pos':e.pos})
                self.send(sub.type,sub)
                container.Container.event(self,sub)
            
    
    def loop(self):
        App.app = self
        s = self.screen
        for e in pygame.event.get():
            if not (e.type == QUIT and self.mywindow):
                self.event(e)
        us = self.update(s)
        pygame.display.update(us)
        
        
    def paint(self,screen):
        self.screen = screen
        if self._chsize:
            self.resize()
            self._chsize = False
        if hasattr(self,'background'):
            self.background.paint(screen)
        container.Container.paint(self,screen)

    def update(self,screen):
        """Update the screen.
        
        <dl>
        <dt>screen<dd>pygame surface
        </dl>
        """
        self.screen = screen
        if self._chsize:
            self.resize()
            self._chsize = False
        if self._repaint:
            self.paint(screen)
            self._repaint = False
            return [pygame.Rect(0,0,screen.get_width(),screen.get_height())]
        else:
            us = container.Container.update(self,screen)
            return us
    
    def run(self,widget=None,screen=None): 
        """Run an application.
        
        <p>Automatically calls <tt>App.init</tt> and then forever loops <tt>App.event</tt> and <tt>App.update</tt></p>
        
        <dl>
        <dt>widget<dd>main widget
        <dt>screen<dd>pygame.Surface to render to
        </dl>
        """
        self.init(widget,screen)
        while not self._quit:
            self.loop()
            pygame.time.wait(10)
    
    def reupdate(self,w=None): pass
    def repaint(self,w=None): self._repaint = True
    def repaintall(self): self._repaint = True
    def chsize(self):
        self._chsize = True
        self._repaint = True
    
    def quit(self,value=None): self._quit = True

class Desktop(App):
    """Create an App using the <tt>desktop</tt> theme class.
    
    <pre>Desktop()</pre>
    """
    def __init__(self,**params):
        params.setdefault('cls','desktop')
        App.__init__(self,**params)