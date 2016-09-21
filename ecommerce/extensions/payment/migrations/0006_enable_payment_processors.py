# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

from ecommerce.extensions.payment.processors.cybersource import Cybersource
from ecommerce.extensions.payment.processors.paypal import Paypal
# Added by EDUlib
from ecommerce.extensions.payment.processors.paysafe import Paysafe
# Added by EDUlib
from ecommerce.extensions.payment.processors.netbanx import Netbanx

def enable_payment_processors(apps, schema_editor):
    """
    Enable existing payment processors.
    """
    Switch = apps.get_model('waffle', 'Switch')
    # Modified by EDUlib, Paysafe added
    for processor in (Cybersource, Paypal, Paysafe, Netbanx):
        Switch(name=settings.PAYMENT_PROCESSOR_SWITCH_PREFIX + processor.NAME, active=True).save()


def delete_processor_switches(apps, schema_editor):
    """
    Remove payment processor switches.
    """
    Switch = apps.get_model('waffle', 'Switch')
    # Modified by EDUlib, Paysafe added
    for processor in (Cybersource, Paypal, Paysafe, Netbanx):
        Switch.objects.get(name=settings.PAYMENT_PROCESSOR_SWITCH_PREFIX + processor.NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_paypalwebprofile'),
    ]

    operations = [
        migrations.RunPython(enable_payment_processors, delete_processor_switches)
    ]
