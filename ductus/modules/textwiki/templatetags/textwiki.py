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
from functools import wraps

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.utils.importlib import import_module
from django.conf import settings

from ductus.wiki.models import WikiPage
from ductus.wiki.namespaces import registered_namespaces

register = template.Library()

def __get_dict_of_possible_module_variables(module_variable_dict):
    if not module_variable_dict:
        return None
    rv = {}
    for key, value in module_variable_dict.iteritems():
        if isinstance(value, basestring):
            mod_name, junk, var_name = value.rpartition('.')
            rv[key] = getattr(import_module(mod_name), var_name)
        else:
            rv[key] = value
    return rv

CREOLEPARSER_BODIED_MACROS = __get_dict_of_possible_module_variables(getattr(settings, "CREOLEPARSER_BODIED_MACROS", None))
CREOLEPARSER_NON_BODIED_MACROS = __get_dict_of_possible_module_variables(getattr(settings, "CREOLEPARSER_NON_BODIED_MACROS", None))

def __wiki_links_class_func(prefix):
    def _wiki_links_class_func(pagename):
        pagename = pagename.partition('#')[0].partition('?')[0]

        wns = registered_namespaces[prefix]
        if wns.page_exists(pagename):
            return "internal"
        else:
            return "internal broken"

    return _wiki_links_class_func

def create_image_path_func(original_path_func):
    @wraps(original_path_func)
    def image_path_func(pagename):
        pathname = original_path_func(pagename).partition('?')[0]
        return "%s?view=image&max_size=250,250" % pathname
    return image_path_func

__interwiki_links_base_urls = None
__interwiki_links_path_funcs = None
__interwiki_links_class_funcs = None

def __prepare_interwiki_links_dicts():
    global __interwiki_links_base_urls, __interwiki_links_path_funcs, __interwiki_links_class_funcs

    if __interwiki_links_base_urls is not None:
        return

    __interwiki_links_base_urls = {}
    __interwiki_links_path_funcs = {}
    __interwiki_links_class_funcs = {}
    for wns in registered_namespaces.itervalues():
        __interwiki_links_base_urls[wns.prefix] = u'/%s/' % wns.prefix
        __interwiki_links_path_funcs[wns.prefix] = (wns.path_func, create_image_path_func(wns.path_func))
        __interwiki_links_class_funcs[wns.prefix] = __wiki_links_class_func(wns.prefix)

@register.filter
@stringfilter
def creole(value, default_prefix=None):
    try:
        from creoleparser.core import Parser
        from creoleparser.dialects import create_dialect, creole11_base
    except ImportError:
        if settings.TEMPLATE_DEBUG:
            raise template.TemplateSyntaxError, "Error in {% creole %} filter: The Python creoleparser library isn't installed."
        return value
    else:
        __prepare_interwiki_links_dicts()
        default_prefix = default_prefix or u'en'
        parser_kwargs = {
            'wiki_links_base_url': '/%s/' % default_prefix,
            'no_wiki_monospace': True,
            'wiki_links_path_func': __interwiki_links_path_funcs[default_prefix],
            'wiki_links_class_func': __wiki_links_class_func(default_prefix),
            'interwiki_links_base_urls': __interwiki_links_base_urls,
            # on the next line, we copy the dict first because creoleparser's
            # create_dialect function modifies it inexplicably! (see
            # creoleparser issue #50)
            'interwiki_links_path_funcs': dict(__interwiki_links_path_funcs),
            'interwiki_links_class_funcs': __interwiki_links_class_funcs,
            'external_links_class': 'external',
            'disable_external_content': True,
        }
        if CREOLEPARSER_BODIED_MACROS:
            parser_kwargs['bodied_macros'] = CREOLEPARSER_BODIED_MACROS
        if CREOLEPARSER_NON_BODIED_MACROS:
            parser_kwargs['non_bodied_macros'] = CREOLEPARSER_NON_BODIED_MACROS
        creole2html = Parser(create_dialect(creole11_base, **parser_kwargs))

        return mark_safe(creole2html(value))

__title_re = re.compile(r'^\s*=+\s*(.*?)\s*=*\s*$', re.MULTILINE | re.UNICODE)

@register.filter
@stringfilter
def creole_guess_title(value):
    s = __title_re.search(value)
    if s:
        return s.group(1)
    else:
        return u''
