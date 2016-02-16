from django import forms
from team.models import Team
from team.models import Venue
from playbyplay.models import Game
import constants


class GamesFilter(forms.Form):
   
    teams = forms.MultipleChoiceField(
        label='Specify Teams', 
        choices=constants.teamNames)
    
    venues = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Venue', queryset=Venue.objects.values_list('name', flat=True), 
        empty_label='All')

    seasons = forms.ModelChoiceField(
        widget=forms.SelectMultiple(attrs={'class' : 'form-control input-sm'}), 
        label='Specify Seasons', 
        queryset=Game.objects.values_list('season', flat=True).distinct(), 
        empty_label=None)
    
    game_type = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class' : 'game-type-checkbox'}), 
        choices=constants.gameTypes, 
        initial=['PR', 'R', 'P', 'A'])

    date_start = forms.DateField(label="Start Date",
        widget=forms.DateInput(attrs={'class': 'form-control input-sm datepicker'}))

    date_end = forms.DateField(label="End Date",
        widget=forms.DateInput(attrs={'class': 'form-control input-sm datepicker'}))


class GameStatsFilter(forms.Form):
    strength = forms.ChoiceField(widget=forms.Select(
        attrs={'class' : 'form-control input-sm'}), 
        label='Team Strength', 
        choices=constants.teamNames)

    score_situation = forms.ChoiceField(
        widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Score Situation', 
        choices=constants.teamNames)

    period = forms.ChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Period', 
        choices=constants.teamNames)
