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

import re
from ductus.urn import resolve_urn

def urn_linkify(html):
    """linkifies URNs

    This function assumes no URNs occur inside HTML tags, as it will attempt to
    linkify them anyway.
    """

    def repl(matchobj):
        urn = matchobj.group(0)
        return u'<a href="%s">%s</a>' % (resolve_urn(urn), urn)

    return re.sub(r'urn:[_\-A-Za-z0-9\:]*', repl, html)
