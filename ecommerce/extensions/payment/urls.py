""" Payment-related URLs """
from django.conf.urls import url

from ecommerce.extensions.payment.views import cybersource, PaymentFailedView
from ecommerce.extensions.payment.views.paypal import PaypalPaymentExecutionView, PaypalProfileAdminView

# Added by EDUlib, added a line for paysafe_notify

######## FICUS
######## faut peut-etre revoir la page de Paysafe??? modificatio dans les appels?
urlpatterns = [
    url(r'^paysafe/notify/page.html$', views.PaysafeNotifyView.as_view(), name='paysafe_notify'),
    url(r'^cybersource/notify/$', cybersource.CybersourceNotifyView.as_view(), name='cybersource_notify'),
    url(r'^cybersource/redirect/$', cybersource.CybersourceInterstitialView.as_view(), name='cybersource_redirect'),
    url(r'^cybersource/submit/$', cybersource.CybersourceSubmitView.as_view(), name='cybersource_submit'),
    url(r'^error/$', PaymentFailedView.as_view(), name='payment_error'),
    url(r'^paypal/execute/$', PaypalPaymentExecutionView.as_view(), name='paypal_execute'),
    url(r'^paypal/profiles/$', PaypalProfileAdminView.as_view(), name='paypal_profiles'),
]
######## FICUS

######### EUCALYPTUS
#########urlpatterns = [
#########    url(r'^paysafe/notify/page.html$', views.PaysafeNotifyView.as_view(), name='paysafe_notify'),
#########    url(r'^cybersource/notify/$', views.CybersourceNotifyView.as_view(), name='cybersource_notify'),
#########    url(r'^paypal/execute/$', views.PaypalPaymentExecutionView.as_view(), name='paypal_execute'),
#########    url(r'^paypal/profiles/$', views.PaypalProfileAdminView.as_view(), name='paypal_profiles'),
#########]
######### EUCALYPTUS
