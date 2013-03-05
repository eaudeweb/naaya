from django.views.generic import View
from django.shortcuts import render, redirect

from tach import models as tach_models
from survey import models as survey_models
from survey import forms as survey_forms
from sugar.views import AuthRequired, AuthDetailsRequired


class Overview(AuthRequired, View):

    def get(self, request):
        form = tach_models.UserForm(instance=request.user)
        return render(request, 'overview.html', {
            'form': form,
        })

    def post(self, request):
        form = tach_models.UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('survey_overview')
        return render(request, 'overview.html', {
            'form': form,
        })


class Survey(AuthDetailsRequired, View):

    def get(self, request):
        sections = survey_models.Survey.objects.filter(
            country=request.user.country)
        categories_section_a = survey_models.Category.objects.filter(
            section__pk=1)
        section_a_form = survey_forms.SectionA()
        return render(request, 'survey.html', {
            'sections': sections,
            'section_a_form': section_a_form,
            'categories_section_a': categories_section_a,
        })
