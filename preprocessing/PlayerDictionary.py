class PlayerDictionary(dict):
    innerDict = {}
    def __init__(self, *args, **kw):
         super(PlayerDictionary,self).__init__(*args, **kw)
         self.itemlist = super(PlayerDictionary,self).keys()
    def __setitem__(self, key, value):
        if self.itemlist.__contains__(key):
            self.__getitem__(key).__setitem__(key,value)
            return
        else:
            copyDict = self.innerDict.copy()
            copyDict.__setitem__(self,"passing",{})
            copyDict.__setitem__(self,"rushing",{})
            copyDict.__setitem__(self,"receiving",{})
        self.itemlist.append(key)
        super(PlayerDictionary,self).__setitem__(key, value)
    def __iter__(self):
         return iter(self.itemlist)
    def keys(self):
         return self.itemlist
    def values(self):
         return [self[key] for key in self]
    def itervalues(self):
         return (self[key] for key in self)