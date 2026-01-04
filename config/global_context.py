from django.utils import timezone

def global_context(request):
    current_year = timezone.now().year
    return {'current_year': current_year}