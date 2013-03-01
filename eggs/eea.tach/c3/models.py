from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class C3(models.Model):

    TRANSPORT_PARTS = (
                ('infrastructure', 'Transport infrastructure'),
                ('services', 'Transport services')
            )

    TRANSPORT_MODES = (
                ('road', 'Road'),
                ('rail', 'Rail'),
                ('aviation', 'Aviation'),
                ('inland_water', 'Inland water shipping'),
                ('maritime', 'Maritime shipping'),
                ('urban_transport', 'Urban transport')
            )

    class Meta:

        db_table = 'c3_table'

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    name = models.CharField(max_length = 256)

    short_information = models.CharField(max_length = 2000)

    parts_considered = MultiSelectField(max_length=256, choices=TRANSPORT_PARTS)

    transport_modes = MultiSelectField(max_length=512, choices=TRANSPORT_MODES)

    website_contact = models.CharField(max_length = 2000)


class C3Form(ModelForm):

    class Meta():

        model = C3

        widgets = {
            'short_information': Textarea(attrs={'cols': 80, 'rows': 3}),
            'website_contact': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

