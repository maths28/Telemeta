from django.forms import Form, FileField

class GenerItemForm(Form):
     fichier = FileField(allow_empty_file=False, label='Selectionnez votre fichier CSV')