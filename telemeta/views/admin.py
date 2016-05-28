# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Samalyse SARL
# Copyright (C) 2010-2012 Parisson SARL

# This file is part of Telemeta.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Authors: Olivier Guilyardi <olivier@samalyse.com>
#          Guillaume Pellerin <yomguy@parisson.com>

from telemeta.views.core import *
from telemeta.forms.generate_item_form import *
from django.conf import settings
import os
from telemeta.models import MediaItem
from django.forms.formsets import formset_factory
import csv
from telemeta.util.tasks import *
from django.http import HttpResponse
import simplejson as json
from django.db.models import Q

class AdminView(object):
    """Provide Admin web UI methods"""

    @method_decorator(permission_required('is_superuser'))
    def admin_index(self, request):
        return render(request, 'telemeta/admin.html', self.__get_admin_context_vars())

    @method_decorator(permission_required('is_superuser'))
    def admin_general(self, request):
        return render(request, 'telemeta/admin_general.html', self.__get_admin_context_vars())

    @method_decorator(permission_required('is_superuser'))
    def admin_enumerations(self, request):
        return render(request, 'telemeta/admin_enumerations.html', self.__get_admin_context_vars())

    @method_decorator(permission_required('is_superuser'))
    def admin_users(self, request):
        users = User.objects.all()
        return render(request, 'telemeta/admin_users.html', {'users': users})

    def __get_enumerations_list(self):
        from django.db.models import get_models
        models = get_models(telemeta.models)

        enumerations = []
        for model in models:
            if issubclass(model, Enumeration):
                if not model.hidden:
                    enumerations.append({"name": model._meta.verbose_name,
                                         "id": model._meta.module_name})

        cmp = lambda obj1, obj2: unaccent_icmp(obj1['name'], obj2['name'])
        enumerations.sort(cmp)
        return enumerations

    def __get_admin_context_vars(self):
        return {"enumerations": self.__get_enumerations_list()}

    def __get_enumeration(self, id):
        from django.db.models import get_models
        models = get_models(telemeta.models)
        for model in models:
            if model._meta.module_name == id:
                break

        if model._meta.module_name != id:
            return None

        return model

    @method_decorator(permission_required('telemeta.change_keyword'))
    def edit_enumeration(self, request, enumeration_id):

        enumeration  = self.__get_enumeration(enumeration_id)
        if enumeration == None:
            raise Http404

        vars = self.__get_admin_context_vars()
        vars["enumeration_id"] = enumeration._meta.module_name
        vars["enumeration_name"] = enumeration._meta.verbose_name
        vars["enumeration_values"] = enumeration.objects.all()
        return render(request, 'telemeta/enumeration_edit.html', vars)

    @method_decorator(permission_required('telemeta.add_keyword'))
    def add_to_enumeration(self, request, enumeration_id):

        enumeration  = self.__get_enumeration(enumeration_id)
        if enumeration == None:
            raise Http404

        enumeration_value = enumeration(value=request.POST['value'],
                                        notes=request.POST["notes"])
        enumeration_value.save()

        return self.edit_enumeration(request, enumeration_id)

    @method_decorator(permission_required('telemeta.change_keyword'))
    def update_enumeration(self, request, enumeration_id):

        enumeration  = self.__get_enumeration(enumeration_id)
        if enumeration == None:
            raise Http404

        if request.method == 'POST':
            enumeration.objects.filter(id__in=request.POST.getlist('sel')).delete()

        return self.edit_enumeration(request, enumeration_id)

    @method_decorator(permission_required('telemeta.change_keyword'))
    def edit_enumeration_value(self, request, enumeration_id, value_id):

        enumeration  = self.__get_enumeration(enumeration_id)
        if enumeration == None:
            raise Http404

        record = enumeration.objects.get(id__exact=value_id)
        content_type = ContentType.objects.get(app_label="telemeta", model=enumeration_id)

        vars = self.__get_admin_context_vars()
        vars["enumeration_id"] = enumeration._meta.module_name
        vars["enumeration_name"] = enumeration._meta.verbose_name
        vars["enumeration_record"] = record
        vars["enumeration_records"] = enumeration.objects.all()
        vars['room'] = get_room(content_type=content_type,
                                   id=record.id,
                                   name=record.value)
        return render(request, 'telemeta/enumeration_edit_value.html', vars)

    @method_decorator(permission_required('telemeta.change_keyword'))
    def update_enumeration_value(self, request, enumeration_id, value_id):

        if request.method == 'POST':
            enumeration  = self.__get_enumeration(enumeration_id)
            if enumeration == None:
                raise Http404

            record = enumeration.objects.get(id__exact=value_id)
            record.value = request.POST["value"]
            record.notes = request.POST["notes"]
            record.save()

        return self.edit_enumeration(request, enumeration_id)

    @method_decorator(permission_required('telemeta.change_keyword'))
    def replace_enumeration_value(self, request, enumeration_id, value_id):
        if request.method == 'POST':
            enumeration = self.__get_enumeration(enumeration_id)
            to_value_id = request.POST["value"]
            delete = False
            if 'delete' in request.POST.keys():
                delete = True

        if enumeration == None:
            raise Http404

        from_record = enumeration.objects.get(id__exact=value_id)
        to_record = enumeration.objects.get(id__exact=to_value_id)
        links = [rel.get_accessor_name() for rel in from_record._meta.get_all_related_objects()]
        field_type = WeakForeignKey

        for link in links:
            objects = getattr(from_record, link).all()
            for obj in objects:
                for name in obj._meta.get_all_field_names():
                    try:
                        field = obj._meta.get_field(name)
                        if type(field) == field_type:
                            if field.rel.to == enumeration:
                                setattr(obj, name, to_record)
                                obj.save()
                    except:
                        continue
        if delete:
            from_record.delete()

        return self.edit_enumeration(request, enumeration_id)


    @method_decorator(permission_required('is_superuser'))
    def generate_items_csv(self, request):
        if request.GET.get('quit', '0') == '1':
            self.remove_file(request.GET.get('file', ''))
        title = "Modification par CSV"
        if request.method == "POST":
            form = GenerItemForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data["file"]
                self.upload_file(file)
                filename = file.name
                attr_form_group = self.generate_attr_form(filename)
                formset = attr_form_group()
                file_form = AboutCSVFileForm(initial={'filename': filename})
        else:
            form = GenerItemForm()
        return render(request, "telemeta/generate_items_csv.html", locals())


    def upload_file(self, file):
        if not os.path.exists(settings.MEDIA_ROOT+'gen_csv'):
            os.mkdir('%sgen_csv' % settings.MEDIA_ROOT, 755)
        with open('%sgen_csv/%s'% (settings.MEDIA_ROOT, file.name), "wb") as filelocal:
            for line in file.chunks():
                filelocal.write(line)

    def remove_file(self, filename):
        if filename is not None:
            os.remove("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))

    def generate_attr_form(self, file):
        file = open("%sgen_csv/%s" % (settings.MEDIA_ROOT, file), "r")
        file_csv = csv.reader(file)
        length = len(next(file_csv))
        file.close()
        return formset_factory(AttributeItemForm, extra=length)

    def valid_attr_form(self, request):
        formset = formset_factory(AttributeItemForm)
        if request.method == "POST":
            form = formset(request.POST)
            file_form = AboutCSVFileForm(request.POST)
            if form.is_valid() and file_form.is_valid():
                list_attr = []
                for f in enumerate(form):
                    attr = f[1].cleaned_data['attribute']
                    if f[0] != 0 and attr not in list_attr:
                         list_attr.append(attr)
                if len(list_attr) != form.total_form_count()-1:
                    return HttpResponse(status=400)
                list_attr.insert(0, form[0].cleaned_data['attribute'])
                filename = file_form.cleaned_data['filename']
                ignore = file_form.cleaned_data['ignore_first_line']
                task = apply_generate_item.delay(list_attr, filename, ignore)
                task_id = task.id
                return HttpResponse(json.dumps({'task_id': task_id}), content_type='application/json')
        return HttpResponse(status=404)

    def progress_task(self, request, task_id):
        result = get_task_status(task_id)
        return HttpResponse(json.dumps(result), content_type='application/json')

    def get_correction_form(self, request):
         if request.method == "POST" and "item" in request.POST.keys() and\
             "attribute" in request.POST.keys():
             attr = request.POST.get('attribute')
             item = request.POST.get('item')
             qs = MediaItem.objects.filter(Q((attr, item)))
             if len(qs) == 1:
                 ItemCodeCorrectionForm = generate_correction_form(attr)
                 form = ItemCodeCorrectionForm(instance=qs[0])
                 return HttpResponse(form.as_p())
         return HttpResponse(status=404)


    def apply_correction(self, request):
        if request.method == "POST":
            attr = request.POST.get('attribute')
            item = request.POST.get(attr)
            ItemCodeCorrection = generate_correction_form(attr)
            qs = MediaItem.objects.filter(Q((attr, item)))
            if len(qs) == 1:
                form = ItemCodeCorrection(request.POST, instance=qs[0])
                if form.is_valid():
                    form.save()
                    return HttpResponse(status=201)
                else:
                    return HttpResponse(form.as_p())
        return HttpResponse(status=404)
