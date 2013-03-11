from json import dumps
from django.views.generic import View
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template import  RequestContext
from django.forms.models import model_to_dict

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
        template = getattr(form, 'VIEW_TEMPLATE', 'view.html')
        return render(request, template, {
            'form': form,
            'survey': survey,
        })


class Edit(View):

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def get(self, request, category_id, survey_id=None):
        if survey_id:
            survey = get_object_or_404(models.Survey, pk=survey_id,
                                       country=request.user.country)
        else:
            survey = None

        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()(
            initial=model_to_dict(survey) if survey else {})
        template = getattr(form, 'EDIT_TEMPLATE', 'form.html')
        return render(request, template, {
            'form': form,
            'category': category,
            'survey': survey,
        })

    @method_decorator(auth_required)
    @method_decorator(auth_details_required)
    def post(self, request, category_id, survey_id=None):
        if survey_id:
            survey = get_object_or_404(models.Survey, pk=survey_id,
                                       country=request.user.country)
        else:
            survey = None

        category = get_object_or_404(models.Category, pk=category_id)
        form = category.get_widget()(request.POST)

        if form.is_valid():
            survey = form.save(user=request.user, country=request.user.country,
                               category=category, survey=survey)
            data =  {'survey': survey, 'category': category}
            response = {
                'status': 'success',
                'html': render_to_string(form.PREVIEW_TEMPLATE, data,
                                         context_instance=RequestContext(request))
            }
            return HttpResponse(dumps(response), mimetype='application/json')


        template = getattr(form, 'EDIT_TEMPLATE', 'form.html')
        data = {'form': form, 'category': category, 'survey': survey}
        response = {
            'status': 'error',
            'html': render_to_string(template, data,
                                     context_instance=RequestContext(request))
        }
        return HttpResponse(dumps(response), mimetype='application/json')
