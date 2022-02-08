"""
Utilities for determining the IP address of a request.
"""

import warnings

from django.conf import settings

# .. setting_name: CLIENT_IP_REQUEST_META_FIELD
# .. setting_default: 'HTTP_X_FORWARDED_FOR'
# .. setting_description: When determining the client's IP address for attribution, tracking, rate-limiting, or other
#   general-purpose needs, draw the IP address from this request.META entry. The entry must be a non-empty list of
#   IP addresses separated by commas, with whitespace tolerated around each address. (The list may be of length 1.)
#   The setting CLIENT_IP_REQUEST_META_INDEX will be used to determine which entry from the list to use. This index
#   will be interpreted via a Python list lookup, so e.g. 0 is the first element and -2 is the second from the end.
#   Most deployers will likely want to use 'HTTP_X_FORWARDED_FOR' index -1, depending on their reverse proxy setup.
#   If the LMS or CMS is directly exposed to the internet, then 'REMOTE_ADDR' index -1 (or 0) would be correct.
#   (Note that for fields only containing a single IP, -1 and 0 are equivalent; the last element is the only
#   element.)
# .. setting_warnings: This must be set in coordination with CLIENT_IP_REQUEST_META_INDEX and with awareness of what
#   proxies are in front of edxapp. Using element 0 of XFF is disrecommended because it will allow malicious callers
#   to spoof their IP address.

# .. setting_name: CLIENT_IP_REQUEST_META_INDEX
# .. setting_default: -1
# .. setting_description: The position in ``request.META[CLIENT_IP_REQUEST_META_FIELD]`` from which to read an IP
#   address when determing the client's IP. Should be set to -1 for most fields. See CLIENT_IP_REQUEST_META_FIELD
#   for more details.
# .. setting_warnings: This must be set in coordination with CLIENT_IP_REQUEST_META_FIELD -- both should be
#   overridden together, or neither.


def get_client_ip(request):
    """
    Determine the IP address of the HTTP client according to settings.

    If the settings are invalid or inconsistent, warn and fall back to
    REMOTE_ADDR, which should always be present (though not necessarily
    *correct*.)
    """
    field = getattr(settings, 'CLIENT_IP_REQUEST_META_FIELD', 'HTTP_X_FORWARDED_FOR')
    index = getattr(settings, 'CLIENT_IP_REQUEST_META_INDEX', -1)

    raw_value = request.META.get(field) or ''
    parts = [s.strip() for s in raw_value.split(',')]
    try:
        client_ip = parts[index]
    except IndexError:
        warnings.warn(
            "Configured index into client IP address field is out of range: "
            f"{field}[{index}] "
            f"(actual length {len(parts)})",
            UserWarning
        )
        client_ip = None
    else:
        if not client_ip:
            warnings.warn("Client IP address settings did not find an IP", UserWarning)

    # This is the only possible fallback we can rely on existing.
    return client_ip or request.META['REMOTE_ADDR']
