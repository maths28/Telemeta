from django.forms import Form, FileField, ValidationError
import os

class GenerItemForm(Form):
     fichier = FileField(label='Selectionnez votre fichier CSV')

     def clean(self):
          cleaned = super(GenerItemForm, self).clean()
          file = cleaned.get('fichier', None)
          if file is None:
              raise ValidationError("Fichier vide !")
          else:
               name = file.name
               ext = os.path.splitext(name)[1]
               if ext.lower() != ".csv":
                    raise ValidationError("Ceci n'est pas un fichier CSV !")
          return cleaned