from django.db import models


class User(models.Model):

    user_id = models.CharField(max_length=128, primary_key=True)

    first_name = models.CharField(max_length=256)

    last_name = models.CharField(max_length=256)

    country = models.ForeignKey('countries.Country')

    affiliation = models.CharField(max_length=512, null=True, blank=True)

    position = models.CharField(max_length=256, null=True, blank=True)

    email = models.EmailField(max_length=256)

    phone = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)