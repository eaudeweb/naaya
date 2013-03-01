from django.db import models
from django import forms


class User(models.Model):

    user_id = models.CharField(max_length=128, primary_key=True)

    first_name = models.CharField(max_length=256, null=True, blank=True)

    last_name = models.CharField(max_length=256, null=True, blank=True)

    country = models.ForeignKey('countries.Country', null=True, blank=True)

    affiliation = models.CharField(max_length=512, null=True, blank=True)

    position = models.CharField(max_length=256, null=True, blank=True)

    email = models.EmailField(max_length=256, null=True, blank=True)

    phone = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class UserForm(forms.ModelForm):

    class Meta:

        model = User
        exclude = ('user_id',)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['country'].required = True
        self.fields['country'].empty_label = None
