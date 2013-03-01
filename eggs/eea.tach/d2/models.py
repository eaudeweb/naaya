from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class D2(models.Model):

    RELEVANCE = (
                ('none', 'None'),
                ('low', 'Low'),
                ('medium', 'Medium'),
                ('high', 'High'),
                ('don_t_know', "Don't know"),
            )

    class Meta:

        db_table = 'd2_table'

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    eu_adaptation_strategy_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    eu_adaptation_strategy_further = models.CharField(max_length = 2000)

    transport_information_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    transport_information_further = models.CharField(max_length = 2000)

    facilitating_trans_national_cooperation_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    facilitating_trans_national_cooperation_further = models.CharField(max_length = 2000)

    facilitating_cooperation_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    facilitating_cooperation_further = models.CharField(max_length = 2000)

    integration_of_cliemate_change_adaptation_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    integration_of_cliemate_change_adaptation_further = models.CharField(max_length = 2000)

    funding_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    funding_further = models.CharField(max_length = 2000)

    revision_of_design_standards_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    revision_of_design_standards_further = models.CharField(max_length = 2000)

    introducing_climate_proof_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    introducing_climate_proof_further = models.CharField(max_length = 2000)

    development_of_methodologies_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    development_of_methodologies_further = models.CharField(max_length = 2000)

    revision_of_data_collection_needs_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    revision_of_data_collection_needs_further = models.CharField(max_length = 2000)

    transport_research_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    transport_research_further = models.CharField(max_length = 2000)


class D2Form(ModelForm):

    class Meta():

        model = D2

        widgets = {
            'lack_of_awareness_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'transport_information_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'facilitating_trans_national_cooperation_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'facilitating_cooperation_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'integration_of_cliemate_change_adaptation_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'funding_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'revision_of_design_standards_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'introducing_climate_proof_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'development_of_methodologies_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'revision_of_data_collection_needs_further': Textarea(attrs={'cols': 80, 'rows': 3}),
            'transport_research_further': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

