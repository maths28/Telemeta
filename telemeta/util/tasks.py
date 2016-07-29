from celery import shared_task
from telemeta.models import MediaItem, MediaCollection
import csv
from django.conf import settings
import os
from time import sleep
from telemeta.forms import MediaItemForm
from django.forms.models import modelform_factory
from collections import Counter
from django.db.models import ForeignKey
import re
import sys

IGNORE_FIELDS_LIST = ["recording_context", "instruments", "file_size", "identifier_id", "channels", "last_modification_date",
                      "samplerate", "identifier_type", "duration", "identifier_note", "instrument_vernacular_names",
                      "year_published", "performers", "thumbnail", "mime_type", "status", "publisher_collection",
                      "physical_format", "description_collection", "original_format", "reference_collection", "publisher",
                      "identifier_date", "keywords", "resolution", "related_media_urls"]

@shared_task
def apply_generate_item(filename):
    print(sys.getfilesystemencoding())
    sys.stdout.flush()
    file = open("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))
    file_csv = csv.DictReader(file)
    nb_items = len([line for line in file_csv if line['code']!=""])
    counter = 0
    file.seek(0)
    file.readline()
    precedent_error = ()
    for line in file_csv:
        if not os.path.exists("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename)):
            break
        if line['code'] != "":
            item = line['code']
            percent = round((float(counter)/float(nb_items))*100, 1)
            apply_generate_item.update_state(state='PROGRESS', meta={'progress': percent, 'item':item, 'counter': counter+1, 'total':nb_items,  'prec_error': precedent_error})
            if len(precedent_error) != 0:
                sleep(0.5)
            precedent_error = ()
            try:
                object = MediaItem.objects.get(code=item)
            except MediaItem.DoesNotExist:
                object = None
            attrs_form = dict()
            for k, v in line.items():
                if k != "" and k!= "code" and k not in IGNORE_FIELDS_LIST:
                    if k == "collection":
                        if re.match("^http://", v):
                            tab = v.split('/')
                            v = tab[-1] if tab[-1] != "" else tab[-2]
                        if re.match("^\d+", v):
                            try:
                                v = MediaCollection.objects.get(id=v).code
                            except MediaCollection.DoesNotExist:
                                pass
                    if is_foreign(k):
                        f = get_field_name(k)
                        criteria_foreign = {f: v}
                        try:
                            value = get_model_foreign(k).objects.get(**criteria_foreign).pk
                        except:
                            value = None
                            apply_generate_item.update_state(state='PROGRESS', meta={'progress': percent, 'item': item,
                                                                                     'counter': counter + 1,
                                                                                     'total': nb_items,
                                                                                     'prec_error': (line['code'], k+" not found !")})
                            sleep(0.5)
                    else:
                        value = v
                    attrs_form[k]=value
            if object is not None:
                MediaItemRestrictForm = modelform_factory(model=MediaItem, form=MediaItemForm, fields=attrs_form.keys())
                f = MediaItemRestrictForm(attrs_form, instance=object)
            else:
                attrs_form['code']=line['code']
                f = MediaItemForm(attrs_form)
            if f.is_valid():
                f.save()
            else:
                precedent_error = (line['code'], str(f.errors))
            counter+=1
    if len(precedent_error) != 0:
        apply_generate_item.update_state(state='PROGRESS',
                                         meta={'progress': 100, 'item': '', 'counter': counter, 'total': nb_items,
                                               'prec_error': precedent_error})
        sleep(0.5)
    file.close()
    os.remove("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))

def is_foreign(field):
    return isinstance(MediaItem._meta.get_field(field), ForeignKey)

def get_field_name(field):
    if is_foreign(field):
        for f in ['code', 'name', 'title', 'value']:
            if f in MediaItem._meta.get_field(field).rel.to._meta.get_all_field_names():
                return f
    return field

def get_model_foreign(field):
    return MediaItem._meta.get_field(field).rel.to

def get_task_status(task_id):

    # If you have a task_id, this is how you query that task
    task = apply_generate_item.AsyncResult(task_id)

    status = task.status
    progress = 0
    item = ""
    counter = 0
    prec_error = ""
    total = 0

    if status == u'SUCCESS':
        progress = 100
    elif status == u'FAILURE':
        progress = 0
    elif status == 'PROGRESS' and task.info is not None:
        try:
            progress = task.info['progress']
            item = task.info['item']
            counter = task.info['counter']
            prec_error = task.info['prec_error']
            total = task.info['total']
        except TypeError:
            progress = 100
            item = ""
            counter = 0
            prec_error = ""
            total = 0

    return {'status': status, 'progress': progress, 'item': item, 'counter': counter, 'total': total, 'prec_error': prec_error}
