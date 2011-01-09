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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from ductus.resource.models import BlueprintSaveContext
from ductus.wiki import SuccessfulEditRedirect
from ductus.wiki.decorators import register_creation_view, register_view, unvarying
from ductus.modules.audio.models import Audio
from ductus.modules.audio.forms import AudioImportForm

@register_creation_view(Audio)
def new_audio(request):
    if request.method == 'POST':
        form = AudioImportForm(request.POST, request.FILES)
        if form.is_valid():
            save_context = BlueprintSaveContext.from_request(request)
            urn = form.save(save_context)
            return SuccessfulEditRedirect(urn)
    else:
        form = AudioImportForm()

    return render_to_response('audio/audio_import_form.html', {
        'form': form,
    }, RequestContext(request))

@register_view(Audio, 'audio')
@unvarying
def view_audio(request):
    audio = request.ductus.resource
    mime_type = audio.blob.mime_type
    data_iterator = iter(audio.blob)

    return HttpResponse(list(data_iterator), # see django #6527
                        content_type=mime_type)

@register_view(Audio)
def view_audio_info(request):
    return render_to_response('audio/display.html', {}, RequestContext(request))

@register_view(Audio, 'edit')
def edit_audio(request):
    return render_to_response('audio/edit.html', {
        'creation_view_key': 'audio',
    }, RequestContext(request))