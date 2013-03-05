from django import forms
from survey.models import Survey


class SectionA(forms.Form):

    status = forms.ChoiceField(choices=Survey.STATUS_CHOICES, widget=forms.RadioSelect)

    title = forms.CharField(max_length=256)

    english_title = forms.CharField(max_length=256, required=False)

    year = forms.IntegerField(required=False)

    parts_considered = forms.MultipleChoiceField(choices=Survey.TRANSPORT_PARTS,
         widget=forms.CheckboxSelectMultiple)

    transport_modes = forms.MultipleChoiceField(choices=Survey.TRANSPORT_MODES,
        widget=forms.CheckboxSelectMultiple)

    climate_change_impacts = forms.MultipleChoiceField(choices=Survey.IMPACTS,
        label='Climate change/extreme weather impact(s) considered for transport (Tick any relevant categories)',
        widget=forms.CheckboxSelectMultiple,)

    responsible_organisation = forms.CharField(max_length=256, required=False)

    link = forms.CharField(max_length=256, required=False)

    def clean_parts_considered(self):
        parts_considered = self.cleaned_data['parts_considered']
        parts_considered_hstore = {i:'1' for i in parts_considered}
        return parts_considered_hstore

    def clean_transport_modes(self):
        transport_modes = self.cleaned_data['transport_modes']
        transport_modes_hstore = {i:'1' for i in transport_modes}
        return transport_modes_hstore

    def clean_climate_change_impacts(self):
        climate_change_impacts = self.cleaned_data['climate_change_impacts']
        climate_change_impacts_hstore = {i:'1' for i in climate_change_impacts}
        return climate_change_impacts_hstore

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            status=self.cleaned_data['status'],
            title=self.cleaned_data['title'],
            english_title=self.cleaned_data['english_title'],
            year=self.cleaned_data['year'],
            parts_considered=self.cleaned_data['parts_considered'],
            transport_modes=self.cleaned_data['transport_modes'],
            climate_change_impacts=self.cleaned_data['climate_change_impacts'],
            responsible_organisation=self.cleaned_data['responsible_organisation'],
            link=self.cleaned_data['link']
        )
        return survey


class SectionB(SectionA):

    def __init__(self, *args, **kwargs):
        pdb
        super(SectionB, self).__init__(*args, **kwargs)

