from django.db import models
from django_hstore import hstore


WIDGETS = {
    'section_a': 'SectionA',
    'section_a_info': 'SectionAInfo',
    'section_a_comment': 'SectionAComment',
    'section_b': 'SectionB',
    'section_b_4': 'SectionB4',
    'section_b_info': 'SectionBInfo',
    'section_b_comment': 'SectionBComment',
    'section_c': 'SectionC',
    'section_c_1_h': 'SectionC1Other',
    'section_c_3': 'SectionC3'
}


class Section(models.Model):

    name = models.CharField(max_length=128)

    class Meta:
        db_table = 'section'


class Category(models.Model):

    title = models.CharField(max_length=256)

    description = models.CharField(max_length=2056)

    section = models.ForeignKey(Section)

    widget = models.CharField(max_length=32)

    for_user = models.BooleanField(default=False)

    multiple_answers = models.BooleanField(default=True)

    class Meta:
        db_table = 'category'
        ordering = ['pk']

    def __unicode__(self):
        return self.title or ''

    def get_widget(self):
        from survey import forms
        widget = getattr(forms, WIDGETS[self.widget])
        return widget


class Language(models.Model):

    iso = models.CharField(max_length=3, primary_key=True)

    title = models.CharField(max_length=64)

    class Meta:
        db_table = 'language'


class Survey(models.Model):

    class Meta:
        db_table = 'survey'

    def __unicode__(self):
        return self.title


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

    language = models.ForeignKey(Language, null=True, blank=True)

    contact = models.CharField(max_length=256, null=True, blank=True)

    focus = models.CharField(max_length=256, null=True, blank=True)

    section_a_info = models.TextField(null=True, blank=True)

    section_a_comment = models.TextField(null=True, blank=True)

    section_b_info = models.TextField(null=True, blank=True)

    objects = hstore.HStoreManager()
