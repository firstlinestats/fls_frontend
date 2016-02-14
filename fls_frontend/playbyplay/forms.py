from django import forms
from team.models import Team
from team.models import Venue
from playbyplay.models import Game
import constants


class GamesFilter(forms.Form):
   
    teams = forms.MultipleChoiceField(label='Specify Teams', choices=constants.teamNames)
    
    venues = forms.ModelChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Venue', queryset=Venue.objects.values_list('name', flat=True), empty_label='All')

    seasons = forms.ModelChoiceField(widget=forms.SelectMultiple(attrs={'class' : 'form-control input-sm'}), 
        label='Specify Seasons', queryset=Game.objects.values_list('season', flat=True).distinct(), empty_label=None)
    
    gameType = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class' : 'game-type-checkbox'}), 
        choices=constants.gameTypes, initial=['PR', 'R', 'P', 'A'])
