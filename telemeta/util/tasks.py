from celery import shared_task
from telemeta.models import MediaItem
import csv
from django.conf import settings
import os
from time import sleep
from telemeta.forms import MediaItemForm
from django.forms.models import modelform_factory
from collections import Counter
from django.db.models import ForeignKey
import sys

@shared_task
def apply_generate_item(fields, filename, ignore_first_line):
    file = open("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))
    file_csv = csv.reader(file)
    nb_items = len([obj[1] for obj in enumerate(file_csv) if (obj[0] != 0 or not ignore_first_line) and obj[1][0] != ""])
    counter = 0
    file.seek(0)
    precedent_error = ()
    for line in file_csv:
        if not os.path.exists("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename)):
            break
        if ignore_first_line:
            ignore_first_line = False
            continue
        if line[0] != "":
            item = line[0]+" ( "+fields[0]+ " )"
            percent = round((float(counter)/float(nb_items))*100, 1)
            criteria = {fields[0]: line[0]}
            apply_generate_item.update_state(state='PROGRESS', meta={'progress': percent, 'item':item, 'counter': counter+1, 'total':nb_items,  'prec_error': precedent_error})
            if len(precedent_error) != 0:
                sleep(0.5)
            precedent_error = ()
            try:
                object = MediaItem.objects.get(**criteria)
            except MediaItem.DoesNotExist:
                object = None
            attrs_form = dict()
            for i in range(1, len(fields)):
                if line[i] != "":
                    if is_foreign(fields[i]):
                        f = get_field_name(fields[i])
                        criteria_foreign = {f: line[i]}
                        try:
                            v = get_model_foreign(fields[i]).objects.get(**criteria_foreign).pk
                        except:
                            v = None
                            apply_generate_item.update_state(state='PROGRESS', meta={'progress': percent, 'item': item,
                                                                                     'counter': counter + 1,
                                                                                     'total': nb_items,
                                                                                     'prec_error': (line[0], fields[i]+" not found !", {})})
                            sleep(0.5)
                    else:
                        v = line[i]
                    print(v)
                    sys.stdout.flush()
                    attrs_form[fields[i]]=v
            if object is not None:
                MediaItemRestrictForm = modelform_factory(model=MediaItem, form=MediaItemForm, fields=attrs_form.keys())
                f = MediaItemRestrictForm(attrs_form, instance=object)
            else:
                attrs_form[fields[0]]=line[0]
                f = MediaItemForm(attrs_form)
            if f.is_valid():
                f.save()
            else:
                res_gen_err = generate_prec_errors(fields, line, f.errors)
                precedent_error = (line[0], res_gen_err[0], res_gen_err[1])
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
        for f in ['name', 'title', 'value']:
            if f in MediaItem._meta.get_field(field).rel.to._meta.get_all_field_names():
                return f
    return field

def get_model_foreign(field):
    return MediaItem._meta.get_field(field).rel.to

def generate_prec_errors(fields_csv, values_csv, errors_form):
    attrs = dict()
    fields_csv = list(fields_csv)
    values_csv = list(values_csv)
    c = Counter(fields_csv)
    if c.get(fields_csv[0]) == 2 or fields_csv[0] in errors_form.keys():
        attrs[fields_csv[0]+"_id"]=values_csv[0]
        del fields_csv[0]
        del values_csv[0]
    for f, e in errors_form.items():
        value = values_csv[fields_csv.index(f)] if f in fields_csv else ""
        attrs[f] = value
    for i, f in enumerate(fields_csv):
        if f not in attrs.keys():
            attrs[f] = values_csv[i]
    import sys
    print(attrs)
    sys.stdout.flush()
    return (str(errors_form), attrs)


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
