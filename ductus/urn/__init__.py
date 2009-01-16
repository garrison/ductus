# Ductus
# Copyright (C) 2008  Jim Garrison <jim@garrison.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.http import HttpResponseRedirect
from ductus.resource import ResourceDatabase

class UnsupportedURN(ValueError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_resource_database():
    global __resource_database
    if __resource_database is None:
        backend = settings.DUCTUS_STORAGE_BACKEND
        mod_name, junk, var_name = backend.rpartition('.')
        storage_backend = getattr(__import__(mod_name, {}, {}, ['']),
                                      var_name)
        __resource_database = ResourceDatabase(storage_backend)
    return __resource_database

__resource_database = None

is_valid_urn = ResourceDatabase.is_valid_urn

def verify_valid_urn(urn):
    """Raises UnsupportedURN if invalid"""

    if not is_valid_urn(urn):
        raise UnsupportedURN(urn)

def resolve_urn(urn):
    """Resolves a URN, returning its absolute URL on the server"""

    verify_valid_urn(urn)
    return u'/%s/' % u'/'.join(urn.split(':'))

class SuccessfulEditRedirect(HttpResponseRedirect):
    """Used by 'edit' views to say that an edit or fork has led to a new URN
    """

    def __init__(self, urn):
        self.urn = urn
        return HttpResponseRedirect.__init__(self, resolve_urn(urn))
