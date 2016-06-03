""" Coupon related utility functions. """
from oscar.core.loading import get_model

from ecommerce.core.url_utils import get_course_catalog_api_client

Product = get_model('catalogue', 'Product')


def get_seats_from_query(site, query, seat_types):
    """
    Retrieve seats from a course catalog query and matching seat types.

    Arguments:
        site (Site): current site
        query (str): course catalog query
        seat_types (str): a string with comma-separated accepted seat type names

    Returns:
        List of seat products retrieved from the course catalog query.
    """
    response = get_course_catalog_api_client(site).course_runs.get(q=query)
    query_products = []
    for result in response['results']:
        try:
            product = Product.objects.get(
                course_id=result['key'],
                attributes__name='certificate_type',
                attribute_values__value_text__in=seat_types.split(',')
            )
            query_products.append(product)
        except Product.DoesNotExist:
            pass
    return query_products


def prepare_course_seat_types(course_seat_types):
    """
    Convert list of course seat types into comma-separated string.
    Arguments:
        course_seat_types (list): List of course seat types
    Returns:
        Comma-separated string.
    """
    if course_seat_types:
        return ','.join(seat_type.lower() for seat_type in course_seat_types)
    return course_seat_types
