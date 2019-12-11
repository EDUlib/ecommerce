#
# Check if the parameter creation for redirection is complete
#

import unittest

from PythonNetBanxSDK.OptimalApiClient import OptimalApiClient
from PythonNetBanxSDK.HostedPayment.Order import Order
from PythonNetBanxSDK.HostedPayment.Redirect import Redirect

import json
import pprint

import random
import string

class RandomTokenGenerator(object):
  def generateToken(self):
    token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
    return (token)

class TestRedirect(unittest.TestCase):
  def test_split(self):
    ##### Create necessary objects
    ### Listing the requested parameters
    ip = '10.8.0.1'
    currency = 'CAD'
    amount = '1125'
    redirecttype = 'on_success'
    redirecturi = 'http://localhost/redirect'
    redirectkey_id = 'id'
    redirectkey_amount = 'transaction.amount'
    refnum = str(RandomTokenGenerator().generateToken())
    
    ### Creating object that will be sent to netbanx
    order_obj = Order(None)
    order_obj.customerIp(ip)
    order_obj.merchantRefNum(refnum)
    order_obj.currencyCode(currency)
    order_obj.totalAmount(amount)
    
    redirect = Redirect(None)
    redirect.rel(redirecttype)
    redirect.uri(redirecturi)
    redirect.returnKeys((redirectkey_id, redirectkey_amount))
    redirect_list = []
    redirect_list.append(redirect.__dict__)
    order_obj.redirect((redirect_list))
    
    ### Check if the function will send all requested parameters
    ## If we want to actually send something, configure the followin and
    ## uncomment the create_order line
    apikey = ""
    apipassword = ""
    apienviro = "TEST"
    apiacnum = ""
    optimal_obj = OptimalApiClient(apikey, apipassword, apienviro, apiacnum)
    #response_object = optimal_obj.hosted_payment_service_handler().create_order(order_obj)
    
    output = optimal_obj.serialize(order_obj)
    parsed_json = json.loads(output)
    pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint("RAW OUTPUT:")
    #pp.pprint(parsed_json)
    
    expected = {'currencyCode':currency, 'customerIp':ip, 'merchantRefNum':refnum, 'redirect':[{'rel':redirecttype, 'returnKeys':[redirectkey_id, redirectkey_amount], 'uri':redirecturi}], 'totalAmount':amount}

    self.assertEqual(parsed_json, expected)

if __name__ == '__main__':
  unittest.main()

