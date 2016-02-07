from django.shortcuts import render

# Create your views here.
def games(request):
    context = {'active_page' : 'games'}
    return render(request, 'playbyplay/games.html', context)