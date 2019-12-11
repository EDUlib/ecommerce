'''
Created on 20-Feb-2015

@author: Asawari.Vaidya
'''

#EDUlib Python 2
#####from PythonNetBanxSDK.common.DomainObject import DomainObject

#EDUlib Python 3
from ecommerce.Paysafe.src.PythonNetBanxSDK.common.DomainObject import DomainObject

class FieldErrors(DomainObject):
    '''
    classdocs
    '''


    def __init__(self, obj):
        '''
        Constructor
        '''
        # Handler dictionary
        handler = dict()
        handler['field'] = self.field
        handler['error'] = self.error
        
        if obj is not None:
            self.setProperties(obj, handler=handler)
        else:
            pass
        
    def field(self, field):
        self.__dict__['field'] = field
        
    def error(self, error):
        self.__dict__['error'] = error
