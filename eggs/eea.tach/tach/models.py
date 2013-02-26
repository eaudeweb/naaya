from django.db import models
from fields import MultiSelectField
from django.forms import ModelForm

class Users(models.Model):
    pass

class A1Types(models.Model):
    title = models.CharField(max_length = 256)

    def __unicode__(self):
        return self.title

class A1(models.Model):
    STATUS_CHOICES = (
                ('approved', 'Approved'),
                ('in_planning', 'In planning'),
                ('not_available', 'Not available')
            )
    TRANSPORT_PARTS = (
                ('infrastructure', 'Transport infrastructure'),
                ('services', 'Transport services')
            )

    entry_type = models.ForeignKey(A1Types)
    status = models.CharField(max_length = 50,
                                choices = STATUS_CHOICES)
    title = models.CharField(max_length = 256)
    english_title = models.CharField(max_length = 256)
    year = models.IntegerField()
    parts_considered = MultiSelectField(max_length=256, choices=TRANSPORT_PARTS)

class A1Form(ModelForm):

    class Meta():
        model = A1

