from django.conf import settings

from ecommerce.core.url_utils import get_lms_dashboard_url, get_lms_url


def core(request):
    return {
        'lms_base_url': get_lms_url(),
        'lms_dashboard_url': get_lms_dashboard_url(),
        'platform_name': request.site.name,
        'support_url': settings.SUPPORT_URL,
    }
