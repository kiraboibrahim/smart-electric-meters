from django.conf import settings
from hashids import Hashids

hashids = Hashids(settings.HASHIDS_SALT, min_length=14)


def h_encode(pk):
    return hashids.encode(pk)


def h_decode(h):
    z = hashids.decode(h)
    if z:
        return z[0]


class HashIdConverter:
    regex = "[a-zA-Z0-9]{8,}"

    def to_python(self, value):
        return h_decode(value)

    def to_url(self, value):
        return h_encode(value)
