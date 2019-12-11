'''
Created on 05-Feb-2015

@author: Asawari.Vaidya
'''

# EDUlib Python 2
#####from PythonNetBanxSDK.common.DomainObject import DomainObject

# EDUlib Python 3
from ecommerce.Paysafe.src.PythonNetBanxSDK.common.DomainObject import DomainObject

class AddendumData(DomainObject):
    '''
    classdocs
    '''
    def __init__(self, obj):
        '''
        Constructor
        '''
        # Handler dictionary
        handler = dict()
        handler['key'] = self.key
        handler['value'] = self.value
        
        if obj is not None:
            self.setProperties(obj, handler=handler)
        else:
            pass
                       
    '''
    Property Key
    '''   
    def key(self, key):
        self.__dict__['key'] = key
        
    '''
    Property Value
    '''   
    def value(self, value):
        self.__dict__['value'] = value
