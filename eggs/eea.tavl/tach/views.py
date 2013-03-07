from django.views.generic import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator

from tach import models as tach_models
from survey import models as survey_models
from survey import forms as survey_forms
from sugar.views import auth_required, auth_details_required


class Overview(View):

    @method_decorator(auth_required)
    def get(self, request):
        form = tach_models.UserForm(instance=request.user)
        return render(request, 'overview.html', {
            'form': form,
        })

    @method_decorator(auth_required)
    def post(self, request):
        form = tach_models.UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('survey_overview')
        return render(request, 'overview.html', {
            'form': form,
        })


class Survey(View):

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def get(self, request):
        sections = survey_models.Survey.objects.filter(
            country=request.user.country)

        # section A
        categories_section_a = survey_models.Category.objects.filter(
            section__pk=1)

        # section B
        categories_section_b = survey_models.Category.objects.filter(
            section__pk=2)

        # section C
        categories_section_c = survey_models.Category.objects.filter(
            section__pk=3)

        # section D
        categories_section_d = survey_models.Category.objects.filter(
            section__pk=4)

        # section E
        categories_section_e = survey_models.Category.objects.filter(
            section__pk=5)
        category_e_comment = categories_section_e[0]
        category_e = categories_section_e[1]

        return render(request, 'survey.html', {
            'sections': sections,
            'categories_section_a': categories_section_a,
            'categories_section_b': categories_section_b,
            'categories_section_c': categories_section_c,
            'categories_section_d': categories_section_d,
            'category_e_comment': category_e_comment,
            'category_e': category_e,
        })
