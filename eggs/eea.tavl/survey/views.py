from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator

from survey import models, forms
from sugar.views import auth_required, auth_details_required


class View(View):

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def get(self, request, category_id, survey_id):
        category = get_object_or_404(models.Category, pk=category_id)
        survey = get_object_or_404(models.Survey, pk=survey_id,
                                   country=request.user.country)
        form = category.get_widget()()
        return render(request, form.VIEW_TEMPLATE, {
            'form': form,
            'survey': survey,
        })


class Edit(View):

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def get(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()()
        return render(request, form.EDIT_TEMPLATE, {
            'form': form,
            'category': category,
        })

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def post(self, request, category_id):
        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()(request.POST)

        if form.is_valid():
            form.save(user=request.user, country=request.user.country,
                      category=category)
            return redirect('survey_overview')

        return render(request, form.EDIT_TEMPLATE, {
            'form': form,
            'category': category,
        })