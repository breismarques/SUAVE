#!/usr/bin/env python

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

from Dict import Dict
from Property import Property

# ----------------------------------------------------------------------
#   Bunch 
# ----------------------------------------------------------------------

class Bunch(Dict):
    """ A dictionary that provides attribute-style access.
        This implementation does not extend __getattribute__ to maintain
        performance.
        
    """
    
    __getitem__ = Dict.__getattribute__
    __setitem__ = Dict.__setattr__
    __delitem__ = Dict.__delattr__
        
    def clear(self):
        self.__dict__.clear()
        
    def copy(self):
        return self.__dict__.copy()
    
    def get(self,k,d=None):
        return self.__dict__.get(k,d)
    
    def has_key(self,k):
        return self.__dict__.has_key(k)
    
    def pop(self,k,d=None):
        return self.__dict__.pop(k,d)
        
    def popitem(self):
        return self.__dict__.popitem()
    
    def setdefault(self,k,d=None):
        self.__dict__.setdefault(k,d)
        
    #def update(self,other):
        #return Dict.update(self,other)
    
    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()
    
    def values(self):
        return self.__dict__.values()
    
    def iteritems(self):
        return self.__dict__.iteritems()
    
    def iterkeys(self):
        return self.__dict__.iterkeys()
    
    def itervalues(self):
        return self.__dict__.itervalues()
    
    def viewitems(self):
        return self.__dict__.viewitems()
    
    def viewkeys(self):
        return self.__dict__.viewkeys()
    
    def viewvalues(self):
        return self.__dict__.viewvalues()
    
    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
    
    def to_dict(self):
        r = {}
        for k,v in self.items():
            if isinstance(v,Bunch):
                v = v.to_dict()
            r[k] = v
        return r
    
    def __cmp__(self,other):
        try:
            return self.__dict__.__cmp__(other)
        except TypeError:
            return False
    
    def __contains__(self,k):
        return self.__dict__.__contains__(k)
    
    def __eq__(self,other):
        return self.__dict__.__eq__(other)
    
    def __ge__(self,other):
        return self.__dict__.__ge__(other)
    
    def __gt__(self,other):
        return self.__dict__.__gt__(other)
    
    def __iter__(self):
        return self.iterkeys()
    
    def __le__(self,other):
        return self.__dict__.__le__(other)
    
    def __len__(self):
        return self.__dict__.__len__()
    
    def __lt__(self,other):
        return self.__dict__.__lt__(other)
    
    def __ne__(self,other):
        return self.__dict__.__ne__(other)
    

# ----------------------------------------------------------------------
#   Module Tests
# ----------------------------------------------------------------------

if __name__ == '__main__':
    
    # load up
    o = Bunch()
    o['x'] = 'hello'
    o.y = 1
    o['z'] = [3,4,5]
    o.t = Bunch()
    o.t['h'] = 20
    o.t.i = (1,2,3)
    
    def test_function(c):
        return c.x
    
    class Operation(Bunch):
        d = Property()
        def __init__(self,f,d):
            self.f = f
            self.d = d
        def __call__(self,*x):
            return self.f(self.d,*x)
    
    o.f = Operation(test_function,o)
    
    # printing
    print o.keys()
    print o
    print o.f()

    # pickling test
    import pickle

    d = pickle.dumps(o)
    p = pickle.loads(d)
    
    print ''
    print p    
    print "should be true:" , p.f.d is p
    
    o.t['h'] = 'changed'
    p.update(o)

    print ''
    print p
    
    # speed test
    from time import time, sleep
    t0 = time()
    for i in range(100000):
        v = o.t.i
    t1 = time()-t0
    
    class SimpleBunch:
        pass
    z = SimpleBunch()
    z.t = SimpleBunch
    z.t.i = 0
    t0 = time()
    for i in range(100000):
        v = z.t.i
    t2 = time()-t0
    
    print 'Bunch:       %.6f' % (t1)
    print 'SimpleBunch: %.6f' % (t2)    
 