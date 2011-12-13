import json

class PyOnJs:
    """
    Inheriting from this class will add a dumps to instances, and loads to the class.
    instance.dumps() dumps out to a json string, where Klass.loads(...) will return an
    instance of Klass initialized from the string.

    Internally this relies upon the default json library in python. What it adds is the
    ability for classes to define _json and _jsonc attributes to control the saving and
    loading of attributes.

    _json must be a list of the names of attributes that will be serialized

    _jsonc is an optional dictionary that maps property names to the types that they
    should be. The types can either be a single class, or a list for custom types nested
    inside lists or dictionaries.  At this point dictionaries can only be strings to
    other types. For example: [list, dict, Klass] would be interpreted as a list of
    dicts that map from strings to instances of Klass.
    """
    def dumps(self):
        return json.dumps(toJSONFriendly(self))
    @classmethod
    def loads(klass, var):
        return fromJSONType(json.loads(var),klass)

def toJSONFriendly(element):
    """
    dumps out objects to dictionaries, lists etc. so pythons json.dumps can be called
    """
    if type(element) == dict:
        return dict([(x,toJSONFriendly(element[x])) for x in element])
    elif type(element) in [list,tuple]:
        return [toJSONFriendly(x) for x in element]
    elif "_json" in element.__class__.__dict__:
        d = {}
        for name in element.__class__._json:
            d[name] = toJSONFriendly(element.__dict__[name])
        return d
    else:
        return element

class JSONParseException(Exception):
    def __init__(self,trace):
        self.trace = trace
        Exception.__init__(self,"Error Parsing:"+".".join(trace))

def fromJSONType(element, klass = None, trace = None):
    """
    Loads in an object from dictionaries/lists etc.

    klass can either be a single class, or a list of classes for chained basic types.
    This is only needed if the leaf classes need to be parsed into objects, not left
    as the dictionaries/lists/primatives that json.loads outputs

    If something unexpected is encountered a JSONParseException is raised

    The objects instantiated will not have __init__ called, they are created with
    __new__ and have attributes set.
    """
    try:
        if type(klass)==list and len(klass)==1:
            klass = klass[0]

        if trace ==None:
            trace = []
            
        if not klass:
            return element

        if type(klass)==list:
            #complex declaration, either a list or a dict
            if klass[0]==list:
                return [fromJSONType(x,klass[1:],trace=trace+["list"]) for x in element]
            elif klass[0]==dict:
                mp = {}
                for eid in element:
                    mp[fromJSONType(eid,trace=trace+["dict"])]=fromJSONType(element[eid],klass[1:],trace=trace+["dict"])
                return mp
            else:
                return element

        elif klass in [tuple,int,str,float]:
            return klass(element)

        elif '_json' in klass.__dict__:
            trace+=[klass.__name__]
            jsonc = {}
            if '_jsonc' in klass.__dict__:
                jsonc = klass._jsonc

            mp = {}
            for name in klass._json:
                if name in jsonc:
                    mp[name] = fromJSONType(element[name],jsonc[name],trace=trace+[name])
                else:
                    mp[name] = fromJSONType(element[name],trace=trace+[name])
            inst = klass.__new__(klass)
            for name in mp:
                inst.__setattr__(name,mp[name])
            return inst
        else:
            return element
    except KeyError as e:
        trace+=[e.args[0]]
        for k in e.__dict__:
            print(k,e.__dict__[k])
        raise JSONParseException(trace)
    
