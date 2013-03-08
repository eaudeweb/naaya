# -*- coding: utf-8

from django import forms
from survey.models import Survey, Language


class SectionA(forms.Form):

    PREVIEW_TEMPLATE = 'section_a/preview.html'

    status = forms.ChoiceField(choices=Survey.STATUS_CHOICES,
                               required=True,
                               widget=forms.RadioSelect)

    title = forms.CharField(max_length=256)

    english_title = forms.CharField(max_length=256, required=False)

    year = forms.IntegerField(required=False)

    parts_considered = forms.MultipleChoiceField(choices=Survey.TRANSPORT_PARTS,
                    label='Part(s) of the transport system considered',
                    help_text='Tick any relevant categories',
                    required=False,
                    widget=forms.CheckboxSelectMultiple)

    transport_modes = forms.MultipleChoiceField(choices=Survey.TRANSPORT_MODES,
                    label='Transport mode(s) considered',
                    help_text='Tick any relevant categories',
                    required=False,
                    widget=forms.CheckboxSelectMultiple)

    climate_change_impacts = forms.MultipleChoiceField(choices=Survey.IMPACTS,
                    label='Climate change/extreme weather impact(s) considered for transport',
                    help_text='Tick any relevant categories',
                    required=False,
                    widget=forms.CheckboxSelectMultiple)

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
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionAInfo(forms.Form):

    EDIT_TEMPLATE = 'form_comment.html'

    PREVIEW_TEMPLATE = 'section_a/preview_comment.html'

    comment = forms.CharField(required=True, widget=forms.Textarea)

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_a_info=self.cleaned_data['comment'],
        )
        return survey


class SectionAComment(SectionAInfo):

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_a_comment=self.cleaned_data['comment'],
        )
        return survey


class SectionBInfo(forms.Form):

    EDIT_TEMPLATE = 'form_comment.html'

    PREVIEW_TEMPLATE = 'section_b/preview_comment.html'

    comment = forms.CharField(required=True, widget=forms.Textarea)

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_b_info=self.cleaned_data['comment'],
        )
        return survey


class SectionBComment(SectionBInfo):

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_b_comment=self.cleaned_data['comment'],
        )
        return survey


class SectionB(SectionA):

    PREVIEW_TEMPLATE = 'section_a/preview.html'

    language = forms.ChoiceField(initial='en')

    contact = forms.CharField(max_length=256, required=False)

    def __init__(self, *args, **kwargs):
        super(SectionB, self).__init__(*args, **kwargs)
        self.fields.pop('status')
        self.fields.pop('english_title')
        req_in_addition_to_a = ('year', 'parts_considered', 'transport_modes',
                         'climate_change_impacts', 'responsible_organisation')
        for req_field in req_in_addition_to_a:
            self.fields[req_field].required = True
        languages = [(l.iso, l.title) for l in Language.objects.all()]
        self.fields['language'].choices = languages

    def save(self, user, country, category):
        language = Language.objects.get(pk=self.cleaned_data['language'])
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            if k == 'language':
                setattr(survey, k, language)
            else:
                setattr(survey, k, v)
        survey.save()
        return survey


class SectionB4(SectionA):

    focus = forms.CharField(max_length=256, required=False,
        label="Focus (e.g. adaptation in general, transport specific, …)")

    def __init__(self, *args, **kwargs):
        super(SectionB4, self).__init__(*args, **kwargs)
        self.fields.pop('status')
        self.fields.pop('english_title')
        req_in_addition_to_a = ('year', 'parts_considered', 'transport_modes',
                         'climate_change_impacts', 'responsible_organisation')
        for req_field in req_in_addition_to_a:
            self.fields[req_field].required = True

    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionC(forms.Form):

    PREVIEW_TEMPLATE = 'section_c/preview.html'

    title = forms.CharField(max_length=256, label="Name")

    link = forms.CharField(max_length=256, label="Website / contact",
                           required=True)

    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionC2(forms.Form):

    EDIT_TEMPLATE = 'form_comment.html'

    PREVIEW_TEMPLATE = 'section_c/preview_comment.html'

    comment = forms.CharField(required=True, widget=forms.Textarea)

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_c2=self.cleaned_data['comment'],
        )
        return survey


class SectionCComment(SectionC2):

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_c_comment=self.cleaned_data['comment'],
        )
        return survey


class SectionC1Other(SectionC):

    responsible_for = forms.CharField(max_length=256)


class SectionC3(SectionA):

    activity_type = forms.CharField(max_length=256,
            label='Short information of type of activity, transport mode, etc.',
            required=False)

    def __init__(self, *args, **kwargs):
        super(SectionC3, self).__init__(*args, **kwargs)
        self.fields.pop('status')
        self.fields.pop('english_title')
        self.fields.pop('year')
        self.fields.pop('climate_change_impacts')
        self.fields.pop('responsible_organisation')
        self.fields['transport_modes'].required = True
        self.fields['parts_considered'].required = True
        self.fields['link'].required = True
        self.fields['title'].label = "Name"
        self.fields['link'].label = "Website / contact"

    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionD1(forms.Form):

    PREVIEW_TEMPLATE = 'section_d/preview.html'

    lack_of_awareness = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            widget=forms.RadioSelect)

    knowledge_gaps = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            widget=forms.RadioSelect)

    data_gaps = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            widget=forms.RadioSelect)

    lack_of_training = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            widget=forms.RadioSelect)

    lack_of_capacities = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Lack of capacities (e.g. appropriate staff)',
            widget=forms.RadioSelect)

    lack_of_resources = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Lack of financial resources',
            widget=forms.RadioSelect)

    access_to_funding = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Difficult access to funding',
            widget=forms.RadioSelect)

    lack_of_coordination = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Lack of coordination or conflicting sectoral policies such as transport-economy-nature protection etc.',
            widget=forms.RadioSelect)

    awareness_lack_eu_level = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Lack of coordination or conflicting policies between different government levels – between the local, regional, national, EU level',
            widget=forms.RadioSelect)

    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionD2(forms.Form):

    PREVIEW_TEMPLATE = 'section_d/preview.html'

    adaptation_strategy = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='EU adaptation strategy',
            widget=forms.RadioSelect)

    transport_information = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Transport information in the Climate ADAPT platform, e.g. risk maps at the European level, guidelines, tools …',
            widget=forms.RadioSelect)

    trans_national_cooperation = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Facilitating trans-national cooperation',
            widget=forms.RadioSelect)

    stakeholders_cooperaton = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Facilitating the cooperation with key stakeholders, bridging the gap among the transport community and climate change scientists',
            widget=forms.RadioSelect)

    integration_of_climate_change = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Integration of climate change adaptation into other EU policy areas (such as cohesion, transport social, and other policies',
            widget=forms.RadioSelect)

    funding = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Funding',
            widget=forms.RadioSelect)

    revision_of_design = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Revision of design standards',
            widget=forms.RadioSelect)

    climate_proof = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Introducing “climate-proof” as a conditionality to support any transport project or policy (e.g. as proposed for EU Structural Funds 2014-2020)',
            widget=forms.RadioSelect)

    development_methodologies = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Development of methodologies, indicators and thresholds on resilience and vulnerabilities',
            widget=forms.RadioSelect)

    data_collection = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Revision of data collection needs and development of new data collection standards',
            widget=forms.RadioSelect)

    transport_research = forms.ChoiceField(choices=Survey.RELEVANT_CHOICES,
            label='Transport research for adaptation to climate change',
            widget=forms.RadioSelect)


    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionDComment(SectionAInfo):

    PREVIEW_TEMPLATE = 'section_c/preview_comment.html'

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_d_comment=self.cleaned_data['comment'],
        )
        return survey


class SectionD1Other(forms.Form):

    PREVIEW_TEMPLATE = 'section_a/preview.html'

    title = forms.CharField(max_length=256, label="Name another barrier")

    relevance = forms.ChoiceField(label="Relevance",
                                  widget=forms.RadioSelect,
                                  choices=Survey.RELEVANT_CHOICES)

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            title=self.cleaned_data['title'],
            relevance=self.cleaned_data['relevance'],
        )
        return survey


class SectionD2Other(SectionD1Other):

    def __init__(self, *args, **kwargs):
        super(SectionD2Other, self).__init__(*args, **kwargs)
        self.fields['title'].label = "Name another activity"


class SectionE(forms.Form):

    PREVIEW_TEMPLATE = 'section_e/preview.html'

    title = forms.CharField(max_length=256, label="Name", required=True)

    area_of_expertise = forms.CharField(widget=forms.Textarea)

    responsible_organisation = forms.CharField(max_length=256, required=False)

    link = forms.CharField(max_length=256, required=False,
                           label="Website and/or address")

    contact = forms.CharField(max_length=256, required=True,
                              label="Contact (email, telephone)")


    def save(self, user, country, category):
        survey = Survey(user=user, country=country, category=category)
        for k, v in self.cleaned_data.items():
            setattr(survey, k, v)
        survey.save()
        return survey


class SectionEComment(SectionAInfo):

    PREVIEW_TEMPLATE = 'section_e/preview_comment.html'

    def save(self, user, country, category):
        survey = Survey.objects.create(
            user=user,
            country=country,
            category=category,
            section_e_comment=self.cleaned_data['comment'],
        )
        return survey
