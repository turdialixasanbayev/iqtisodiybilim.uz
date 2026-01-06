from category.models import Tag, Category
from django.utils import timezone

def global_context(request):
    current_year = timezone.now().year
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return {'current_year': current_year, 'categories': categories, 'tags': tags}