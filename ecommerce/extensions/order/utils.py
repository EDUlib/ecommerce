"""Order Utility Classes. """
from __future__ import unicode_literals
import logging

from oscar.apps.order.utils import OrderCreator as OscarOrderCreator
from oscar.core.loading import get_model
from threadlocals.threadlocals import get_current_request

from ecommerce.referrals.models import Referral

logger = logging.getLogger(__name__)

Order = get_model('order', 'Order')


class OrderNumberGenerator(object):
    # Modified by EDUlib
    OFFSET = 100000
    #OFFSET = 500000
    #OFFSET = 501000
    # Modified by EDUlib

    def order_number(self, basket):
        """
        Returns an order number, determined using the basket's ID and site.

        Arguments:
            basket (Basket)

        Returns:
            string: Order number
        """
        site = basket.site
        if not site:
            site = get_current_request().site
            logger.warning('Basket [%d] is not associated with a Site. Defaulting to Site [%d].', basket.id, site.id)

        partner = site.siteconfiguration.partner
        return self.order_number_from_basket_id(partner, basket.id)

    def order_number_from_basket_id(self, partner, basket_id):
        """
        Return an order number for a given basket ID.

        Arguments:
            basket_id (int): Basket identifier.

        Returns:
            string: Order number.
        """
        order_id = int(basket_id) + self.OFFSET
        return u'{prefix}-{order_id}'.format(prefix=partner.short_code.upper(), order_id=order_id)

    def basket_id(self, order_number):
        """Inverse of order number generation.

        Given an order number, returns the basket ID used when generating it.

        Arguments:
            order_number (str): An order number.

        Returns:
            int: The basket ID used to generate the provided order number.
        """
        
        # Added by EDUlib
        #logger.info("order_number is %s", order_number)
        # Added by EDUlib

        order_id = int(order_number.split('-')[1])
        return order_id - self.OFFSET


class OrderCreator(OscarOrderCreator):
    def create_order_model(self, user, basket, shipping_address, shipping_method, shipping_charge, billing_address,
                           total, order_number, status, **extra_order_fields):
        """
        Create an order model.

        This override ensures the order's site is set to that of the basket. If the basket has no site, the default
        site is used. The site value can be overridden by setting the `site` kwarg.
        """

        # Added by EDUlib
        #print("---------------------------")
        #print("Entering create_order_model")
        #print("---------------------------")
        # Added by EDUlib

        # If a site was not passed in with extra_order_fields,
        # use the basket's site if it has one, else get the site
        # from the current request.
        site = basket.site
        if not site:
            site = get_current_request().site
            
        # Added by EDUlib
        #print("===== valeur de site =====")
        #print(site)
        #print("===== valeur de site =====")

        #print("===== valeur de total =====")
        #print(total)
        #print("===== valeur de total =====")
        # Added by EDUlib

        order_data = {'basket': basket,
                      'number': order_number,
                      'site': site,
                      'currency': total.currency,
                      'total_incl_tax': total.incl_tax,
                      'total_excl_tax': total.excl_tax,
                      'shipping_incl_tax': shipping_charge.incl_tax,
                      'shipping_excl_tax': shipping_charge.excl_tax,
                      'shipping_method': shipping_method.name,
                      'shipping_code': shipping_method.code}
        if shipping_address:
            order_data['shipping_address'] = shipping_address
        if billing_address:
            order_data['billing_address'] = billing_address
        if user and user.is_authenticated():
            order_data['user_id'] = user.id
        if status:
            order_data['status'] = status
        if extra_order_fields:
            order_data.update(extra_order_fields)
        order = Order(**order_data)
        order.save()
        
        # Added by EDUlib
        #print("--------------------------")
        #print("Leaving create_order_model")
        #print("--------------------------")
        # Added by EDUlib

        # not in the version of ecommerce we tried
        #try:
        #    referral = Referral.objects.get(basket=basket)
        #    referral.order = order
        #    referral.save()
        #except Referral.DoesNotExist:
        #    logger.debug('Order [%d] has no referral associated with its basket.', order.id)
        #except Exception:  # pylint: disable=broad-except
        #    logger.exception('Referral for Order [%d] failed to save.', order.id)

        return order
