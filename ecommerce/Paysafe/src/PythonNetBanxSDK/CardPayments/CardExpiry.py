'''
Created on 05-Feb-2015

@author: Asawari.Vaidya
'''

# EDUlib Python 2
#####from PythonNetBanxSDK.common.DomainObject import DomainObject

# EDUlib Python 3
from ecommerce.Paysafe.src.PythonNetBanxSDK.common.DomainObject import DomainObject

class CardExpiry(DomainObject):
    '''
    classdocs
    '''

    def __init__(self, obj):
        '''
        Constructor
        '''
        # Handler dictionary
        handler = dict()
        handler['month'] = self.month
        handler['year'] = self.year

        
        if obj is not None:
            self.setProperties(obj, handler=handler)
        else:
            pass
        
    '''
    Property Month
    '''
    def month(self, month):
        self.__dict__['month'] = month
        
    '''
    Property Year
    '''
    def year(self, year):
        self.__dict__['year'] = year
