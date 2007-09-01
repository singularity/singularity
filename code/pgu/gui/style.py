"""
"""

class Style:
    """The class used by widget for the widget.style
    
    <p>This object is used mainly as a dictionary, accessed via <tt>widget.style.attr</tt>, as opposed to
    <tt>widget.style['attr']</tt>.  It automatically grabs information from the theme via <tt>value = theme.get(widget.cls,widget.pcls,attr)</tt>.</p>
    
    """
    def __init__(self,o,dict):
        self.obj = o
        for k,v in dict.items(): self.__dict__[k]=v
        self._cache = {}
        
    def __getattr__(self,k):
        key = self.obj.cls,self.obj.pcls,k
        if key not in self._cache:
            #import app
            #self._cache[key] = app.App.app.theme.get(self.obj.cls, self.obj.pcls, k)
            self._cache[key] = Style_get(self.obj.cls,self.obj.pcls,k)
        v = self._cache[key]
        if k in (
            'border_top','border_right','border_bottom','border_left',
            'padding_top','padding_right','padding_bottom','padding_left',
            'margin_top','margin_right','margin_bottom','margin_left',
            'align','valign','width','height',
            ): self.__dict__[k] = v
        return v
        
    def __setattr__(self,k,v):
        self.__dict__[k] = v
        
        
Style_cache = {}
def Style_get(cls,pcls,k):
    key = cls,pcls,k
    if key not in Style_cache:
        import app
        Style_cache[key] = app.App.app.theme.get(cls,pcls,k)
    return Style_cache[key]
        
