from django.forms import Form, FileField, ValidationError, ChoiceField,\
    CharField, BooleanField, ModelForm, TextInput
import os
import csv
from telemeta.models import MediaItem
from django.forms.models import modelform_factory

class GenerItemForm(Form):
     file = FileField(label='Selectionnez votre file CSV')

     def clean(self):
          cleaned = super(GenerItemForm, self).clean()
          file = cleaned.get('file', None)
          if file is None:
              raise ValidationError("Le fichier ne doit pas etre vide")
          else:
               name = file.name
               ext = os.path.splitext(name)[1]
               if ext.lower() != ".csv":
                    raise ValidationError("Le fichier doit etre un CSV (.csv)")
               else:
                    file_csv = csv.reader(file.file)
                    if len(next(file_csv)) < 2:
                         raise ValidationError("Au moins deux attributs doivent etre renseignes")
          return cleaned

def list_attributes():
    attrs = MediaItem._meta.get_all_field_names()
    list_attrs = []
    for attr in attrs:
        list_attrs.append((attr, attr))

    return list_attrs

class AttributeItemForm(Form):

    attribute = ChoiceField(choices=list_attributes())

class AboutCSVFileForm(Form):

    filename = CharField(required=True)
    ignore_first_line = BooleanField(required=False, label='Ignore the first line ?')


def generate_correction_form(id_attr):
    return modelform_factory(MediaItem, fields=(id_attr, "code"),
                      widgets={id_attr: TextInput(attrs={'readonly': 'readonly'})})
