from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from survey import models, forms
from sugar.views import AuthDetailsRequired


class SectionA(AuthDetailsRequired, View):

    def get(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = forms.SectionA()
        return render(request, 'section_a/form.html', {
            'form': form,
            'category': category,
        })

    def post(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = forms.SectionA(request.POST)
        if form.is_valid():
            form.save(user=request.user, country=request.user.country,
                      category=category)
            return redirect('survey_overview')

        return render(request, 'section_a/form.html', {
            'form': form,
            'category': category,
        })