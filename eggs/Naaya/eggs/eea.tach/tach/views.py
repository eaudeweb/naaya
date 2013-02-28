from django.views.generic import View
from django.shortcuts import render
import a1
import b1
import c1
import c3
import d1
import d2
from expert import models as expert_models

class Survey(View):
    def get(self, request):
        form_a1 = a1.models.A1Form()
        form_b1 = b1.models.B1Form()
        form_c1 = c1.models.C1Form()
        form_c3 = c3.models.C3Form()
        form_d1 = d1.models.D1Form()
        form_d2 = d2.models.D2Form()
        return render(request, 'survey.html', {
            'form_a1': form_a1,
            'form_b1': form_b1,
            'form_c1': form_c1,
            'form_c3': form_c3,
            'form_d1': form_d1,
            'form_d2': form_d2,
        })

    def post(self, request):
        pass
        #form = a1models.A1Form(request.POST)
        #if form.is_valid():
        #    form.save()
        #return render(request, 'survey.html', {'form': form})

