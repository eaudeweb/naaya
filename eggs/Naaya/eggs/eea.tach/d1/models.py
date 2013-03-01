from django.db import models
from sugar.models import MultiSelectField
from django.forms import ModelForm, Textarea


class D1(models.Model):

    RELEVANCE = (
                ('none', 'None'),
                ('low', 'Low'),
                ('medium', 'Medium'),
                ('high', 'High'),
                ('don_t_know', "Don't know"),
            )

    class Meta:

        db_table = 'd1_table'

    country = models.ForeignKey('countries.Country')

    user = models.ForeignKey('tach.User')

    lack_of_awareness_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_awareness_details = models.CharField(max_length = 2000)

    knowledge_gaps_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    knowledge_gaps_details = models.CharField(max_length = 2000)

    data_gaps_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    data_gaps_details = models.CharField(max_length = 2000)

    lack_of_training_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_training_details = models.CharField(max_length = 2000)

    lack_of_capabilities_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_capabilities_details = models.CharField(max_length = 2000)

    lack_of_financial_resources_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_financial_resources_details = models.CharField(max_length = 2000)

    difficult_access_to_funding_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    difficult_access_to_funding_details = models.CharField(max_length = 2000)

    lack_of_coordination_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_coordination_details = models.CharField(max_length = 2000)

    lack_of_government_coordination_relevance = models.CharField(max_length = 50,
                                choices = RELEVANCE)
    lack_of_government_coordination_details = models.CharField(max_length = 2000)


class D1Form(ModelForm):

    class Meta():

        model = D1

        widgets = {
            'lack_of_awareness_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'knowledge_gaps_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'data_gaps_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'lack_of_training_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'lack_of_capabilities_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'lack_of_financial_resources_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'difficult_access_to_funding_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'lack_of_coordination_details': Textarea(attrs={'cols': 80, 'rows': 3}),
            'lack_of_government_coordination_details': Textarea(attrs={'cols': 80, 'rows': 3}),
        }

