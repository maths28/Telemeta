from django.forms import Form, FileField, ValidationError, ChoiceField,\
    CharField, BooleanField, TextInput
import os
import csv
from telemeta.models import MediaItem
from django.forms.models import modelform_factory
from telemeta.forms import MediaItemForm

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
                    line = next(file_csv)
                    if len(line) < 2:
                         raise ValidationError("Au moins deux attributs doivent etre renseignes")
                    elif "code" not in line:
                         raise ValidationError("Le champ cote est obligatoire dans le fichier")
          return cleaned

