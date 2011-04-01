# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
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

from ductus.resource import ductmodels, register_ductmodel
from ductus.util import create_property

class WikiBlobElement(ductmodels.TextBlobElement):
    allowed_markup_languages = ('creole-1.0',)
    allowed_natural_languages = (None, '') + zip(*settings.DUCTUS_NATURAL_LANGUAGES)[0]
    markup_language = ductmodels.Attribute(validator=ductmodels.allowed_values_attribute_validator(allowed_markup_languages))
    natural_language = ductmodels.Attribute(validator=ductmodels.allowed_values_attribute_validator(allowed_natural_languages), optional=True, blank_is_null=True)

    def __init__(self):
        # fixme: if Attribute had a "default" argument, we wouldn't need to
        # override this constructor to set such a default
        super(WikiBlobElement, self).__init__()
        self.markup_language = "creole-1.0"

@register_ductmodel
class Wikitext(ductmodels.DuctModel):
    ns = 'http://wikiotics.org/ns/2009/wikitext'
    blob = WikiBlobElement()

    @create_property
    def text():
        def fget(s):
            return b''.join(s.blob).decode('utf-8')
        def fset(s, v):
            s.blob.store([v.encode('utf-8')])
        return locals()