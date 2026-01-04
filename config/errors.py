from django.shortcuts import render
from django.views import View


class PageNotFoundView(View):
    def get(self, request, exception=None):
        return render(request, '404.html', status=404)
