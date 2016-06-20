""" Payment-related URLs """
from django.conf.urls import url

from ecommerce.extensions.payment import views

# Added by EDUlib, added a line for netbanx_notify
urlpatterns = [
    url(r'^netbanx/notify/page.html$', views.NetbanxNotifyView.as_view(), name='netbanx_notify'),
    url(r'^cybersource/notify/$', views.CybersourceNotifyView.as_view(), name='cybersource_notify'),
    url(r'^paypal/execute/$', views.PaypalPaymentExecutionView.as_view(), name='paypal_execute'),
    url(r'^paypal/profiles/$', views.PaypalProfileAdminView.as_view(), name='paypal_profiles'),
]
