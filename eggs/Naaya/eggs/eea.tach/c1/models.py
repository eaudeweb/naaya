from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class C1Type(models.Model):

    title = models.CharField(max_length=256)

    class Meta:

        db_table = 'c1_type'

    def __unicode__(self):
        return self.title


class C1(models.Model):

    class Meta:

        db_table = 'c1_table'

    entry_type = models.ForeignKey(C1Type)

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    name = models.CharField(max_length = 256)

    website = models.CharField(max_length = 256)


class C1Form(ModelForm):

    class Meta():

        model = C1

