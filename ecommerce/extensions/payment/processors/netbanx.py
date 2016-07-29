""" Netbanx payment processing. """
from __future__ import unicode_literals

import datetime
import logging
import uuid
from decimal import Decimal

# PIERRE
# a ajouter pour Netbanx
from urlparse import urljoin
from django.core.urlresolvers import reverse
import pprint
# a ajouter pour Netbanx

from django.conf import settings
from oscar.apps.payment.exceptions import UserCancelled, GatewayError, TransactionDeclined
from oscar.core.loading import get_model
from suds.client import Client
from suds.sudsobject import asdict
from suds.wsse import Security, UsernameToken
from threadlocals.threadlocals import get_current_request

from ecommerce.core.url_utils import get_lms_url
from ecommerce.core.constants import ISO_8601_FORMAT
from ecommerce.extensions.order.constants import PaymentEventTypeName
from ecommerce.extensions.payment.constants import CYBERSOURCE_CARD_TYPE_MAP
from ecommerce.extensions.payment.exceptions import (InvalidSignatureError, InvalidNetbanxDecision,
                                                     PartialAuthorizationError)
from ecommerce.extensions.payment.helpers import sign
from ecommerce.extensions.payment.processors import BasePaymentProcessor
from ecommerce.extensions.payment.transport import RequestsTransport

# PIERRE
# a ajouter pour Netbanx
from PythonNetBanxSDK.OptimalApiClient import OptimalApiClient
from PythonNetBanxSDK.HostedPayment.Order import Order
from PythonNetBanxSDK.HostedPayment.Refund import Refund
from PythonNetBanxSDK.CustomerVault.Profile import Profile

import random
import string

import sqlite3
# a ajouter pour Netbanx

logger = logging.getLogger(__name__)

PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventType = get_model('order', 'PaymentEventType')
PaymentProcessorResponse = get_model('payment', 'PaymentProcessorResponse')
ProductClass = get_model('catalogue', 'ProductClass')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')

# PIERRE
# a ajouter pour Netbanx
# on remet le random ici
class RandomTokenGenerator(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def generateToken(self):
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        return (token)
# a ajouter pour Netbanx


class Netbanx(BasePaymentProcessor):
    """
    Faudrait mettre les bons liens vers la documentation de Netbanx
    """

    NAME = 'netbanx'

    def __init__(self):
        """
        Constructs a new instance of the CyberSource processor.

        Raises:
            KeyError: If no settings configured for this payment processor
            AttributeError: If LANGUAGE_CODE setting is not set.
        """

        configuration = self.configuration

        ##### PIERRE
        ##### juste besoin de celles-ci dans local.py dans settings
        ##### reprendre api_password comme secret_key pour la signature
        ##### optimal_obj = OptimalApiClient(Config.api_key, Config.api_password, Config.environment, Config.account_number)
        ##### api_key = 'devcentre4133'
        ##### api_password =  'B-qa2-0-54b640bb-302c0214635160e36f364d9f710be900436db25cc5cb0efe021448eb9731ced8a09cb73283050d48a8acb5c4e395'
        ##### account_number = '89983967'
        ##### environment = 'TEST'
        self.language_code = settings.LANGUAGE_CODE
        self.api_key = configuration['api_key']
        self.api_password = configuration['api_password']
        self.environment = configuration['environment']
        self.account_number = configuration['account_number']
        self.secret_key = configuration['api_password']
        self.ecommerce_path = configuration['ecommerce_path']

    @property
    def receipt_page_url(self):
        return get_lms_url(self.configuration['receipt_path'])

    @property
    def cancel_page_url(self):
        return get_lms_url(self.configuration['cancel_path'])

    def get_transaction_parameters(self, basket, request=None):
        """
        Generate a dictionary of signed parameters Netbanx requires to complete a transaction.

        Arguments:
            basket (Basket): The basket of products being purchased.

        Keyword Arguments:
            request (Request): A Request object which could be used to construct an absolute URL; not
                used by this method.

        Returns:
            dict: Netbanx-specific parameters required to complete a transaction, including a signature.
        """

        print("-----------------------------------")
        print("Entering get_transaction_parameters")
        print("-----------------------------------")

        # PIERRE
        # quelques changements pour parameters afin d'utiliser ceux necessaires pour netbanx
        parameters = {
            'signed_date_time': self.utcnow().strftime(ISO_8601_FORMAT),
            'locale': self.language_code,
            'transaction_type': 'sale',
            'reference_number': basket.order_number,
            'amount': str(basket.total_incl_tax),
            'currency': basket.currency,
            'consumer_id': basket.owner.username,
            'override_custom_receipt_page': 'http://test-cours.edulib.org/commerce/checkout/receipt/?orderNum={}'.format(basket.order_number),
            'override_custom_cancel_page': self.cancel_page_url,
            'payment_page_url' : None,
            'pierre': None,
        }

        # PIERRE
        # a-t-on vraiment besoin de cette section-ci pour XCOM-274?
        '''
        # XCOM-274: when internal reporting across all processors is
        # operational, these custom fields will no longer be needed and should
        # be removed.
        single_seat = self.get_single_seat(basket)
        if single_seat:
            parameters['merchant_defined_data1'] = single_seat.attr.course_key
            parameters['merchant_defined_data2'] = getattr(single_seat.attr, 'certificate_type', '')

        amount = 0
        # Level 2/3 details
        if self.send_level_2_3_details:
            parameters['amex_data_taa1'] = '{}'.format(get_current_request().site.name)
            parameters['purchasing_level'] = '3'
            parameters['line_item_count'] = basket.lines.count()
            # Note (CCB): This field (purchase order) is required for Visa;
            # but, is not actually used by us/exposed on the order form.
            parameters['user_po'] = 'BLANK'

            for index, line in enumerate(basket.lines.all()):
                parameters['item_{}_code'.format(index)] = line.product.get_product_class().slug
                parameters['item_{}_discount_amount '.format(index)] = str(line.discount_value)
                # Note (CCB): This indicates that the total_amount field below includes tax.
                parameters['item_{}_gross_net_indicator'.format(index)] = 'Y'
                parameters['item_{}_name'.format(index)] = line.product.title
                parameters['item_{}_quantity'.format(index)] = line.quantity
                parameters['item_{}_sku'.format(index)] = line.stockrecord.partner_sku
                parameters['item_{}_tax_amount'.format(index)] = str(line.line_tax)
                parameters['item_{}_tax_rate'.format(index)] = '0'
                parameters['item_{}_total_amount '.format(index)] = str(line.line_price_incl_tax_incl_discounts)
                # Note (CCB): Course seat is not a unit of measure. Use item (ITM).
                parameters['item_{}_unit_of_measure'.format(index)] = 'ITM'
                parameters['item_{}_unit_price'.format(index)] = str(line.unit_price_incl_tax)
                amount = amount + line.unit_price_incl_tax

        # Sign all fields
        signed_field_names = parameters.keys()
        parameters['signed_field_names'] = ','.join(sorted(signed_field_names))
        parameters['signature'] = self._generate_signature(parameters)

        parameters['payment_page_url'] = self.payment_page_url
        '''

        # PIERRE
        # Netbanx object creation
        logger.info("avant appel de OptimalApiClient")
        optimal_obj = OptimalApiClient(self.api_key, self.api_password, self.environment, self.account_number)
        logger.info("apres appel de OptimalApiClient")

        # PIERRE
        # valeurs de configuration
        logger.info("valeurs recuperees du fichier local.py dans settings")
        logger.info("self.api_key = %s, self.api_password = %s, self.account_number =  %s", self.api_key, self.api_password, self.account_number)

        order_obj = Order(None)

        # PIERRE
        # valeurs du basket en cours
        logger.info("valeurs recuperees du basket")
        logger.info("basket.order_number = %s, basket.currency = %s, basket.total_incl_tax = %s", basket.order_number, basket.currency, basket.total_incl_tax)

        order_obj.merchantRefNum(basket.order_number)
        order_obj.currencyCode(basket.currency)

        # PIERRE
        # il faudra jouer sur le montant pour le formatter pour netbanx
        # il faut changer le montant de 34.56 a 3456 par exemple
        # noter utilisation de '' autour de la valeur car sinon prix a 0.64 si on met 0100 sans les single quote
        # petit algorithme: valeur * 100 (valeur est un entier), donc 50 * 100 = 5000, donc 50 pour netbanx        
        new_total = int(basket.total_incl_tax * 100)
        new_total = str(new_total)
        order_obj.totalAmount(unicode(new_total))

        profile_obj = Profile(None)

        # PIERRE
        # il faut changer le merchantCustomerId chaque fois
        # dans les sample applications il y a une generation avec un random
        # nous utiliserons la meme chose
        profile_obj.merchantCustomerId(str(RandomTokenGenerator().generateToken()))

        order_obj.profile(profile_obj)

        # PIERRE
        # ne fonctionne pas avec les returnKeys
        # je recois id seulement lors du create order
        # je force une valeur bidon
        redirect = [{
          "rel":'on_success',
          'returnKeys': [ "merchantRefNum", "id" ],
          'uri':  urljoin(self.ecommerce_path, "{}?orderNum={}&id={}".format(reverse('netbanx_notify'), basket.order_number, "Pierre1964")),
          'delimiter': '&',
        }]
        order_obj.redirect(redirect)

        # PIERRE
        # ne fonctionne pas avec les returnKeys
        # je recois id seulement lors du create order
        # je force une valeur bidon
        callback_def = [{
          'format': 'json',
          'returnKeys': ["merchantRefNum", "id"],
          'uri':  urljoin(self.ecommerce_path, "{}?orderNum={}&id={}".format(reverse('netbanx_notify'), basket.order_number, "this_is_a_string_too")),
          'retries': 1,
        }]
        order_obj.callback(callback_def)

        logger.info("--------------------")
        logger.info("calling create_order")
        logger.info("--------------------")
        response_object = optimal_obj.hosted_payment_service_handler().create_order(order_obj)

        print ("Create Order Response: ")
        print (response_object.__dict__)
        logger.info("---------------------------")
        logger.info("returning from create_order")
        logger.info("---------------------------")

        parameters['payment_page_url'] = response_object.link[0].uri
        parameters['id'] = response_object.id

        # PIERRE
        # Where can I store response_object.id for each transaction? 20160524
        logger.info("id de netbanx = %s", response_object.id)
        logger.info("consumer_id = %s", parameters['consumer_id'])
        logger.info("reference_number = %s", parameters['reference_number'])
        reference = parameters['reference_number']

        ##### TEST 31 05 2016 #####
        conn = sqlite3.connect('/home/ubuntu/ecommerce/ecommerce/extensions/payment/processors/test.db')
        print "Opened database successfully";

        conn.execute("INSERT INTO NETBANX (REFNUM, ID) values (?, ?)", (reference, response_object.id))

        conn.commit()
        print "Records created successfully";
        conn.close()
        ##### TEST 31 05 2016 #####

        print("----------------------------------")
        print("Leaving get_transaction_parameters")
        print("----------------------------------")
 
        # PIERRE
        # je devrais mettre response_object dans une valeur globale
        print("before leaving get_transaction_parameters")
        print(parameters)

        return parameters

    @staticmethod
    def utcnow():
        """
        Returns the current datetime in UTC.

        This is primarily here as a test helper, since we cannot mock datetime.datetime.
        """
        return datetime.datetime.utcnow()

    @staticmethod
    def get_single_seat(basket):
        """
        Return the first product encountered in the basket with the product
        class of 'seat'.  Return None if no such products were found.
        """
        try:
            seat_class = ProductClass.objects.get(slug='seat')
        except ProductClass.DoesNotExist:
            # this occurs in test configurations where the seat product class is not in use
            return None

        for line in basket.lines.all():
            product = line.product
            if product.get_product_class() == seat_class:
                return product

        return None

    def handle_processor_response(self, response, basket=None):
        """
        Handle a response (i.e., "merchant notification") from Netbanx.

        This method does the following:
            1. Verify the validity of the response.
            2. Create PaymentEvents and Sources for successful payments.

        Arguments:
            response (dict): Dictionary of parameters received from the payment processor.

        Keyword Arguments:
            basket (Basket): Basket being purchased via the payment processor.

        Raises:
            UserCancelled: Indicates the user cancelled payment.
            TransactionDeclined: Indicates the payment was declined by the processor.
            GatewayError: Indicates a general error on the part of the processor.
            InvalidNetbanxDecision: Indicates an unknown decision value.
                Known values are ACCEPT, CANCEL, DECLINE, ERROR.
            PartialAuthorizationError: Indicates only a portion of the requested amount was authorized.
        """

        # PIERRE
        # Traces
        logger.info("----------------------------------")
        logger.info("Entering handle_processor_response")
        logger.info("----------------------------------")

        # PIERRE
        # Create Source to track all transactions related to this processor and order
        source_type, __ = SourceType.objects.get_or_create(name=self.NAME)

        # PIERRE
        # valeur forcee pour le moment
        # on peut prendre la valeur du basket
        currency = basket.currency
        print("currency = %s", currency)

        # PIERRE
        # valeur forcee pour le moment
        # on peut prendre la valeur du basket
        total = Decimal(basket.total_incl_tax)
        print("total = %s", total)

        ##### TEST 31 05 2016 #####
        conn = sqlite3.connect('/home/ubuntu/ecommerce/ecommerce/extensions/payment/processors/test.db')
        print "Opened database successfully";

        cursor = conn.execute("SELECT REFNUM, ID from NETBANX WHERE REFNUM=:valeur", {"valeur": basket.order_number})
        for row in cursor:
            print "REFNUM = ", row[0]
            print "ID = ", row[1],  "\n"

        transaction_id = row[1]
        print("===== valeur de transaction_id dans get de views.py =====")
        print(transaction_id)
        print("===== valeur de transaction_id dans get de views.py =====")

        print "Operation done successfully";
        conn.close()
        ##### TEST 31 05 2016 #####


        # PIERRE
        # valeur maintenant prise du TEST 31 05 2016
        print("transaction_id = %s", transaction_id)

        # PIERRE
        # modifie pour Netbanx
        source = Source(source_type=source_type,
                        currency=currency,
                        amount_allocated=total,
                        amount_debited=total,
                        reference=transaction_id)

        # Create PaymentEvent to track
        event_type, __ = PaymentEventType.objects.get_or_create(name=PaymentEventTypeName.PAID)
        event = PaymentEvent(event_type=event_type, amount=total, reference=transaction_id, processor_name=self.NAME)

        logger.info("---------------------------------")
        logger.info("Leaving handle_processor_response")
        logger.info("---------------------------------")

        return source, event

    def issue_credit(self, source, amount, currency):

        # PIERRE
        # traces
        # amount et currency en entrant ici
        print("Entering issue_credit")
        print("issue_credit amount")
        print(amount)
        print("issue_credit currency")
        print(currency)

        # PIERRE
        # modification du montant pour Netbanx
        new_amount = int(amount * 100)
        print("issue_credit new_amount")
        print(new_amount)

        # PIERRE
        # recuperation du ref number chez Netbanx
        order_request_token = source.reference
        print("issue_credit order_request_token")
        print(order_request_token)

        # PIERRE
        # ne semble pas connaitre objet Refund
        # fallait ajouter from PythonNetBanxSDK.HostedPayment.Refund import Refund
        # creation objets refund et order
        print("issue_credit refund creating refund_obj and order_obj")
        refund_obj = Refund(None)
        order_obj = Order(None)

        # PIERRE
        # pourquoi regeneration de notre ref num?
        # est-ce que ce serait pas notre EDX-machin?
        # pas selon la documentation
        print("issue_credit refund creating merchantRefNum")
        refund_obj.merchantRefNum(RandomTokenGenerator().generateToken())

        # PIERRE
        # ajout du montant a rembourser
        print("issue_credit de amount")
        print(new_amount)
        refund_obj.amount(new_amount)

        # PIERRE
        # Traces
        print("before refund id")
        
        # PIERRE
        # valeur forcee pour le moment
        # comment obtenir la bonne valeur?
        # c'est le order_request_token de plus haut
        #####order_obj.id("27GNRPZIOUAULKA1LK") # pourquoi une valeur forcee ici?
        order_obj.id(order_request_token)

        # PIERRE
        logger.info("just before \"refund_obj.Order(order_obj)\"")
        refund_obj.order(order_obj)      ##### <----- this works
        #### grosse difference si order au lieu de Order
        #### c'est order dans la classe pas Order SHIT
        logger.info("before call to refund_order")

        # PIERRE
        # obtenir les valeurs de la configuration au lieu de les forcer ici
        self._optimal_obj = OptimalApiClient(api_key='devcentre4133',
                                             api_password='B-qa2-0-54b640bb-302c0214635160e36f364d9f710be900436db25cc5cb0efe021448eb9731ced8a09cb73283050d48a8acb5c4e395',
                                             env='TEST',
                                             account_number='89983967')
        response_object = self._optimal_obj.hosted_payment_service_handler().refund_order(refund_obj)

        # PIERRE
        # Traces
        logger.info("after call to refund_order")
        logger.info("valeur de response_object")
        # valeur nulle
        print(response_object)
        logger.info("valeur de response_object")
        order = source.order

        print("Leaving issue_credit")

def suds_response_to_dict(d):  # pragma: no cover
    """
    Convert Suds object into serializable format.

    Source: http://stackoverflow.com/a/15678861/592820
    """
    out = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = suds_response_to_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(suds_response_to_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out
