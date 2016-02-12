from django import forms
from team.models import Team
from team.models import Venue
from playbyplay.models import Game
import constants

class GamesFilter(forms.Form):
   
    teams = forms.MultipleChoiceField(label='Teams', choices=constants.teamNames)
    
    venues = forms.ModelChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Venue', queryset=Venue.objects.all().order_by('name'), empty_label='All')

    seasons = forms.ModelChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Seasons', queryset=Game.objects.values_list('season', flat=True).distinct(), empty_label=None)
    
    session = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class' : 'session-checkbox'}), 
        choices=constants.gameTypes)