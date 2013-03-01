from django.views.generic import View
from django.shortcuts import render


class Overview(View):

    def get(self, request):
        return render(request, 'overview/index.html', {

        })