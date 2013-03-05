from django.db import models
from django_hstore import hstore

class Section(models.Model):

    name = models.CharField(max_length=128)

    class Meta:
        db_table = 'section'


class Category(models.Model):

    title = models.CharField(max_length=256)

    description = models.CharField(max_length=2056)

    section = models.ForeignKey(Section)

    multiple_answers = models.BooleanField(default=True)

    widget = models.CharField(max_length=128)


    class Meta:
        db_table = 'category'
        ordering = ['pk']

    def __unicode__(self):
        return self.title

    def get_widget(self, instance=None):
        from survey import forms
        form = getattr(forms, self.widget, None)
        return form(instance=instance) if form else None


class Survey(models.Model):

    class Meta:
        db_table='survey'

    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('in_planning', 'In planning'),
        ('not_available', 'Not available'),
    )

    TRANSPORT_PARTS = (
        ('infrastructure', 'Transport infrastructure'),
        ('services', 'Transport services'),
    )

    TRANSPORT_MODES = (
        ('road', 'Road'),
        ('rail', 'Rail'),
        ('aviation', 'Aviation'),
        ('inland_water', 'Inland water shipping'),
        ('maritime', 'Maritime shipping'),
        ('urban_transport', 'Urban transport'),
    )

    IMPACTS = (
        ('temperatures', '(Extreme) Temperatures'),
        ('flooding', 'Flooding'),
        ('sea_level_rise', 'Sea level rise'),
        ('storms', 'Storms'),
        ('ice_snow', 'Ice and snow'),
        ('water_scarcity_droughts', 'Water scarcity and droughts'),
    )

    category = models.ForeignKey(Category)

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    # section = models.ForeignKey(Section)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True,
                            blank=True)

    title = models.CharField(max_length=256, null=True, blank=True)

    english_title = models.CharField(max_length=256, null=True, blank=True)

    year = models.IntegerField(null=True, blank=True)

    parts_considered = hstore.DictionaryField(null=True, blank=True )

    transport_modes = hstore.DictionaryField(null=True, blank=True)

    climate_change_impacts = hstore.DictionaryField(null=True, blank=True)

    responsible_organisation = models.CharField(max_length=256, null=True,
                                                blank=True)

    link = models.CharField(max_length=256, null=True, blank=True)

    objects = hstore.HStoreManager()
