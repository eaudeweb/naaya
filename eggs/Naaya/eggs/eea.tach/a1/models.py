from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm


class A1Type(models.Model):

    title = models.CharField(max_length=256)

    class Meta:
        db_table = 'a1_type'

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
    TRANSPORT_MODES = (
                ('road', 'Road'),
                ('rail', 'Rail'),
                ('aviation', 'Aviation'),
                ('inland_water', 'Inland water shipping'),
                ('maritime', 'Maritime shipping'),
                ('urban_transport', 'Urban transport')
            )
    IMPACTS = (
            ('temperatures', '(Extreme) Temperatures'),
                ('flooding', 'Flooding'),
                ('sea_level_rise', 'Sea level rise'),
                ('storms', 'Storms'),
                ('ice_snow', 'Ice and snow'),
                ('water_scarcity_droughts', 'Water scarcity and droughts')
            )

    class Meta:
        db_table = 'a1_table'

    entry_type = models.ForeignKey(A1Type)
    country = models.ForeignKey('countries.Country')
    status = models.CharField(max_length = 50,
                                choices = STATUS_CHOICES)
    title = models.CharField(max_length = 256)
    english_title = models.CharField(max_length = 256)
    year = models.IntegerField()
    parts_considered = MultiSelectField(max_length=256, choices=TRANSPORT_PARTS)
    transport_modes = MultiSelectField(max_length=512, choices=TRANSPORT_MODES)
    climate_change_impacts = MultiSelectField(max_length=512, choices=IMPACTS,
            verbose_name='Climate change/extreme weather impact(s) considered for transport (Tick any relevant categories)')
    responsible_organisation = models.CharField(max_length = 256)
    link = models.CharField(max_length = 256)


class A1Form(ModelForm):

    class Meta():
        model = A1

