"""
Created on Tue Jun  8 13:16:17 2021

@author: DW
"""

import inspect

class Parent(type):
    
    _fields =['aname', 'outsidename']
    
    def __prepare__(name, bases, **kwargs):
        print(f'__prepare ,name {name}, bases{bases}, kwargs {kwargs}')
        return kwargs
    
    
    def __new__(mcls, name, bases, cls_dict, **kwargs):
        print(f"Called __new ({mcls} ),name {name}, bases{bases}, cls_dict {cls_dict} kwargs {kwargs}")
        # print(f'vars: {vars(cls)}')
        
        # kwargs_ = {k : val for k,val in cls_dict.items() if k in mcls._fields}
        _cls_dict_field_kwargs = {}
        for field in mcls._fields:
            ''' 
            in this part the incoming child class attributes that are in parent mcls _fields
            will be deleted and if there is an attribute with the same key in the parent mcls
            then it will be checked for isinstance property and this property is set with the 
            same key in the cls dict before instantiation.
            '''
        
            # if field == 'outsidename':
                # breakpoint()
            if field in cls_dict.keys():
                cls_aname = cls_dict[field]
                _cls_dict_field_kwargs.update({field: cls_aname})
                del cls_dict[field]
                if hasattr(mcls, field):
                    _obj = getattr(mcls, field)
                    if isinstance(_obj, property):
                        cls_dict[field] = _obj
                # TODO !!! Solution was just adding the property from metaclass to the class dict BEFORE instantiation!!!
                
                
                print(f'__new__ del cls_dict {field}, {cls_aname}')
                # setattr(cls_object,'aname', cls_aname)
        # print(f'__new cls obj init: {cls_object.__init__}')
        
        
        print(f'__new cls_dict before init cls object {cls_dict}')
        cls_object = super().__new__(mcls, name, bases, cls_dict)
        setattr(cls_object,'_fields', mcls._fields)
        
        print(f'__new dir mcls {mcls.filter_method(dir(mcls))}\n')
        print(f'__new dir cls_dict {mcls.filter_method(cls_dict.keys())}\n')
        print(f'__new dir cls_obj {mcls.filter_method(dir(cls_object))}\n')
        
        for _field in cls_object._fields:
            if hasattr(cls_object, _field):
                _child_aname = getattr(cls_object,_field)
                print(f'__new getattr {_field} inside from child {_child_aname }, {type(_child_aname )}')
        
        @property
        def aname(self):
            print('=== aname getter is called')
            return self._aname
    
        @aname.setter
        def aname(self, value):
            if len(value) < 4:
                self._aname = value
            else:
                raise ValueError(f'value {value} is too long')
        
        
        methods = inspect.getmembers(mcls, inspect.isdatadescriptor)
        print(f'__new inspect methods {methods}\n')
        
        print(f'__new dir mcls {mcls.filter_method(dir(mcls))}\n')
        print(f'__new dir cls_dict {mcls.filter_method(cls_dict.keys())}\n')
        print(f'__new dir cls_obj {mcls.filter_method(dir(cls_object))}\n')
        
        print(f'__new dir cls_obj __dict__ {mcls.filter_method(cls_object.__dict__)}\n')
        
        
        print(f'__new setattr inside {aname}, {type(aname)}')
        setattr(cls_object,'aname', aname)
        
        
        setattr(cls_object,'_cls_dict_field_kwargs', _cls_dict_field_kwargs)
        
        
        if not '__init__' in cls_dict.keys():
            def init_(self,**kwargs):
                print(f'__init__ {self.__class__} mod called {kwargs}')
                # super()
                methods = inspect.getmembers(self.__class__, inspect.isdatadescriptor)
                print(f'__init Child inspect methods {methods}\n')
                if hasattr(self,'_cls_dict_field_kwargs'):
                    for k,val in self._cls_dict_field_kwargs.items():
                        print(f'__init__ Child mod setattr {k}, {val}')
                        
                        setattr(self, k, val)
            setattr(cls_object,'__init__', init_)
            print(f'__new cls obj new init set:', cls_object.__init__)
        
        
        def repr_(self):
            field_values = (getattr(self, field) for field in self._fields)
            field_val_join = ', '.join(map(str, field_values))
            return f'{self.__class__.__name__}, {field_val_join}'
            # return f'{self.__name__}({field_val_join})'
        setattr(cls_object, '__repr__', repr_)
        
        _other_methods = [i for i in dir(mcls) if not i.startswith('_') and not i == 'mro']
        print(f'__new other methods found: {_other_methods}')
        for method in _other_methods:
            _obj = getattr(mcls, method)
            
            if isinstance(_obj, property):
                # print(f'__new setting other methods set property: {method}, {_obj}')
                pass
                # print('__new setting property {_obj.__get__}')
                # _prop = property(_obj.__get__, _obj.__set__)
                # method = _prop 
                # delattr(cls_object, method)
                # mcls.__setattr__(cls_object, method, _obj)
                # setattr(cls_object, f'{method}.__set__', _obj.__set__)
                # setattr(cls_object, f'{method}.__get__', _obj.__get__)
                # TODO check standard setattr for properties....
                # cls_object.method = _obj
            else:
                print(f'__new setting other methods set: {method}, {_obj}')
                setattr(cls_object, method, _obj)
            # cls_object.__init_
        methods = inspect.getmembers(cls_object, inspect.isdatadescriptor)
        print(f'__new dir cls_obj {methods}\n')
        
        return cls_object
    
    def __init__(self, name, bases, cls_dict, **kwargs):
        print(f'__init__ Parent {name} called {self} going to super')
        # methods = inspect.getmembers(self.__class__, inspect.isdatadescriptor)
        # print(dir(self))
        # for nm, mobj in methods:
        #     if not nm.startswith('__'):
        #         setattr(self,nm,mobj)
        
        methods = inspect.getmembers(self, inspect.isdatadescriptor)
        print(f'__init Parent inspect methods {methods}\n')
        super().__init__(name, bases, cls_dict, **kwargs)
        # self.other_method(self, 2)
        
        pass
    @property
    def outsidename(self):
        return self._outsidename
        # if hasattr(self, '_outsidename'):
        #     _get =getattr(self,'_outsidename')
        #     if len(_get) > 6:
        #         _get = _get[0:4]
        # else:
        #     _get = 'nOnE'
        # return _get
    
    @outsidename.setter
    def outsidename(self, value):
        if not isinstance(value, property):
            if len(value) < 6:
                self._outsidename = value
            else:
                raise ValueError(f'value {value} is too long')
        else:
            pass
            # self._outsidename = None
    @classmethod
    def filter_method(cls, _lst):
        _clean = [i for i in _lst if not i.startswith('_') and not i == 'mro']
        return _clean

    def other_method(self, arg):
        print(f'other method called by {self} with {arg}')

    # def __init_subclass__(cls):
        # print(f'__init_subclass_ Parent called {cls}')
    
    
class Child(metaclass=Parent):
    ''' This is a special docstring for testing purposes'''
    
    aname = 't22'
    outsidename = '2111.'
    # _outsidename = 'g....ood.'


ch = Child()
print('Class repr:',repr(ch))

ch.aname
ch.__class__.aname
ch.__class__

print(ch)
try:
    ch.outsidename = 'no0o00o0o'
except ValueError:
    print("ValueError caught for outsidename = no0o0o")
    
try:
    ch.aname = 'no0o00o0o'
except ValueError:
    print("ValueError caught for aname = no0o0o")
# ch2 = Child(kwa=2)
# print('Class repr : ',repr(ch2))


def _test():
    class Child3(metaclass=Parent, aname='333',outsidename='long'):
        pass
    ch3 = Child3()
# class Child2(metaclass=Parent):
    
#     aname_ = 'tol'
    
#     def __init__(self):
#         self.aname = self.aname_