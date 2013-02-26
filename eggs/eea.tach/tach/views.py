from django.views.generic import View
from django.shortcuts import render
from tach import models

class Survey(View):
    def get(self, request):
        form = models.A1Form()
        return render(request, 'survey.html', {'form': form})

    def post(self, request):
        form = models.A1Form(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'survey.html', {'form': form})

