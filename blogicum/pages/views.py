from django.shortcuts import render


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)


def about(request):
    template = 'pages/about.html'
    return render(request, template)
