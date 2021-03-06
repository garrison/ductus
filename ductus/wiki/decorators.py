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

from functools import wraps

from django.utils.decorators import available_attrs

from ductus.wiki import registered_views, registered_creation_views, registered_subviews, registered_mediacache_views

def register_view(model, label=None, requires=(lambda d: d.resource)):
    """Registers a URN view function.
    """

    fqn = None if model is None else model.fqn
    if requires is None:
        requires = lambda d: True # accept everything; no requirements
    def _register_view(func):
        # make a new function so the decorator doesn't have side effects
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        wrapped_func.meets_requirements = requires # boolean function
        registered_views.setdefault(fqn, dict())[label] = wraps(func, assigned=available_attrs(func))(wrapped_func)
        return func
    return _register_view

def register_creation_view(model, description=None, category=None):
    def _register_creation_view(func):
        if model.root_name in registered_creation_views:
            raise Exception("A model is already registered with this root_name: %s"
                            % registered_creation_views[model.root_name])
        # make a new function so the decorator doesn't have side effects
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        wrapped_func.name = model.root_name
        wrapped_func.description = description
        wrapped_func.category = category
        wrapped_func.do_not_call_in_templates = True
        registered_creation_views[model.root_name] = wraps(func, assigned=available_attrs(func))(wrapped_func)
        return func
    return _register_creation_view

def register_subview(model, label):
    """Registers a URN subview function.
    """

    fqn = None if model is None else model.fqn
    def _register_subview(func):
        registered_subviews.setdefault(fqn, dict())[label] = func
        return func
    return _register_subview

def register_mediacache_view(model):
    """Registers a mediacache view
    """

    def _register_mediacache_view(func):
        registered_mediacache_views[model.fqn] = func
        return func
    return _register_mediacache_view
