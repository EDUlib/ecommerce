'''
Created on 05-Feb-2015

@author: Asawari.Vaidya
'''

# EDUlib Python 2
#####from PythonNetBanxSDK.common.DomainObject import DomainObject

# EDUlib Python 3
from ecommerce.Paysafe.src.PythonNetBanxSDK.common.DomainObject import DomainObject

class AncillaryFee(DomainObject):
    '''
    classdocs
    '''
    def __init__(self, obj):
        '''
        Constructor
        '''
        # Handler dictionary
        handler = dict()
        handler['amount'] = self.amount
        handler['description'] = self.description
        
        if obj is not None:
            self.setProperties(obj, handler=handler)
        else:
            pass
        
    '''
    Property Amount
    '''   
    def amount(self, amount):
        self.__dict__['amount'] = amount
        
    '''
    Property Descriptor
    '''   
    def descriptor(self, descriptor):
        self.__dict__['descriptor'] = descriptor
