from django.shortcuts import render
from django.views import View


class CategoryPage(View):
    def get(self, request):
        return render(request, 'category.html')
