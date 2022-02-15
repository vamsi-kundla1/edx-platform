"""
Middleware to identify the country of origin of page requests.

Middleware adds `country_code` in session.

Usage:

# To enable the Geoinfo feature on a per-view basis, use:
decorator `django.utils.decorators.decorator_from_middleware(middleware_class)`

"""
import ipaddress
import logging

from django.utils.deprecation import MiddlewareMixin

from openedx.core.djangoapps.util.ip import get_client_ip

from .api import country_code_from_ip

log = logging.getLogger(__name__)


class CountryMiddleware(MiddlewareMixin):
    """
    Identify the country by IP address.
    """
    def process_request(self, request):
        """
        Identify the country by IP address.

        Store country code in session.
        """
        new_ip_address = get_client_ip(request)
        old_ip_address = request.session.get('ip_address', None)

        if not new_ip_address and old_ip_address:
            del request.session['ip_address']
            del request.session['country_code']
        elif new_ip_address != old_ip_address and is_public_ip(new_ip_address):
            country_code = country_code_from_ip(new_ip_address)
            request.session['country_code'] = country_code
            request.session['ip_address'] = new_ip_address
            log.debug('Country code for IP: %s is set to %s', new_ip_address, country_code)


def is_public_ip(ip_str):
    """
    Return True if string represents a public IP address, or False if
    in private address space or malformed.
    """
    try:
        return ipaddress.ip_address(ip_str).is_global
    except ValueError:
        return False
