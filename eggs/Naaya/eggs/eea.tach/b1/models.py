from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class B1Type(models.Model):

    title = models.CharField(max_length=256)

    class Meta:
        db_table = 'b1_type'

    def __unicode__(self):
        return self.title


class B1(models.Model):
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
        db_table = 'b1_table'

    entry_type = models.ForeignKey(B1Type)
    country = models.ForeignKey('countries.Country')
    title = models.CharField(max_length = 256)
    language = models.CharField(max_length = 256)
    year = models.IntegerField()
    parts_considered = MultiSelectField(max_length=256, choices=TRANSPORT_PARTS)
    transport_modes = MultiSelectField(max_length=512, choices=TRANSPORT_MODES)
    climate_change_impacts = MultiSelectField(max_length=512, choices=IMPACTS,
            verbose_name='Climate change/extreme weather impact(s) considered for transport (Tick any relevant categories)')
    organisation_author = models.CharField(max_length = 512)
    contact = models.CharField(max_length = 512)
    links = models.CharField(max_length = 512)


class B1Form(ModelForm):

    class Meta():
        model = B1
        widgets = {
            'organisation_author': Textarea(attrs={'cols': 80, 'rows': 3}),
            'contact': Textarea(attrs={'cols': 80, 'rows': 3}),
            'links': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

