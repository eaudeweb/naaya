from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class Expert(models.Model):

    class Meta:

        db_table = 'expert_table'

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    name = models.CharField(max_length = 256)

    area_of_expertise = models.CharField(max_length = 512)

    organisation = models.CharField(max_length = 256)

    website_address = models.CharField(max_length = 2000)

    contact_email_telephone = models.CharField(max_length = 2000)


class ExpertForm(ModelForm):

    class Meta():

        model = Expert

        widgets = {
            'website_address': Textarea(attrs={'cols': 80, 'rows': 3}),
            'contact_email_telephone': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

