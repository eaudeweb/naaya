from django.views.generic import View
from django.shortcuts import render, redirect

from tach import models
from sugar.views import AuthorizationRequired


class Overview(AuthorizationRequired, View):

    def get(self, request):
        form = models.UserForm(instance=request.user)
        return render(request, 'overview/index.html', {
            'form': form,
        })

    def post(self, request):
        form = models.UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('survey')
        return render(request, 'overview/index.html', {
            'form': form,
        })
