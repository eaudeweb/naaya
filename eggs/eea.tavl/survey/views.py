from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from survey import models, forms
from sugar.views import AuthDetailsRequired


class SectionA(AuthDetailsRequired, View):

    def get(self, request, category_id, survey_id):
        category = get_object_or_404(models.Category, pk=category_id)
        survey = get_object_or_404(models.Survey, pk=survey_id,
                                   country=request.user.country)
        form = forms.SectionA()
        return render(request, 'section_a/view.html', {
            'form': form,
            'survey': survey,
        })


class SectionAEdit(AuthDetailsRequired, View):

    def get(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()()
        return render(request, 'section_a/form.html', {
            'form': form,
            'category': category,
        })

    def post(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()(request.POST)
        template = '%s/form.html' % category.widget

        if form.is_valid():
            form.save(user=request.user, country=request.user.country,
                      category=category)
            return redirect('survey_overview')

        return render(request, template, {
            'form': form,
            'category': category,
        })