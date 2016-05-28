from celery import shared_task
from telemeta.models import MediaItem
import csv
from django.conf import settings
from django.db.models import Q
import os
from django.db import IntegrityError
from time import sleep

@shared_task
def apply_generate_item(fields, filename, ignore_first_line):
    file = open("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))
    file_csv = csv.reader(file)
    nb_items = len([obj[1] for obj in enumerate(file_csv) if obj[0] != 0 and obj[1][0] != ""])
    counter = 0
    file.seek(0)
    precedent_error = ()
    for line in file_csv:
        if ignore_first_line:
            ignore_first_line = False
            continue
        if line[0] != "":
            item = line[0]+" ( "+fields[0]+ " )"
            percent = round((float(counter)/float(nb_items))*100, 1)
            criteria = (fields[0]+'__exact', line[0])
            apply_generate_item.update_state(state='PROGRESS', meta={'progress': percent, 'item':item, 'counter': counter+1, 'total':nb_items,  'prec_error': precedent_error})
            if len(precedent_error) != 0:
                sleep(0.5)
            precedent_error = ()
            qs = MediaItem.objects.filter(Q(criteria))
            if len(qs) == 1:
                object = qs[0]
                for i in range(1, len(fields)):
                    if line[i] != "":
                        setattr(object, fields[i], line[i])
                try:
                    object.save()
                except IntegrityError as e:
                    precedent_error = (line[0], e.args[1])
            counter+=1
    if len(precedent_error) != 0:
        apply_generate_item.update_state(state='PROGRESS',
                                         meta={'progress': 100, 'item': '', 'counter': counter, 'total': nb_items, 
                                               'prec_error': precedent_error})
        sleep(0.5)
    file.close()
    os.remove("%sgen_csv/%s" % (settings.MEDIA_ROOT, filename))

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
