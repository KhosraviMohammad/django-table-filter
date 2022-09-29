from django.shortcuts import render

# Create your views here.

def library_view(request):
    context = {}
    return render(request, template_name='example/library.html', context=context)
