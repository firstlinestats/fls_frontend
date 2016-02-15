from django import forms


from playbyplay.models import PlayerGameStats, Game
from playbyplay.constants import homeAway, teamNames, gameTypes

from player.models import Player
from player.constants import skaterPositions

from team.models import Venue


class PlayerStatsFilter(forms.Form):
    teams = forms.MultipleChoiceField(label='Specify Current Teams',
        choices=teamNames)
    venues = forms.ModelMultipleChoiceField(label='Specify Venues',
        queryset=Venue.objects.values_list('name', flat=True))
    home_or_away = forms.ChoiceField(choices=homeAway, initial=2,
        label="Home or Away",
        widget=forms.Select(attrs={'class': 'form-control input-sm'}))
    toi = forms.IntegerField(min_value=0, label="Time On Ice",
        widget=forms.NumberInput(attrs={'class': 'form-control input-sm'}))
    position = forms.MultipleChoiceField(label='Position',
        choices=skaterPositions)
    seasons = forms.ModelChoiceField(
        widget=forms.SelectMultiple(
            attrs={'class' : 'form-control input-sm'}), 
        label='Specify Seasons',
        queryset=Game.objects.values_list('season', flat=True)\
            .distinct(), empty_label=None)
    game_type = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={'class' : 'game-type-checkbox'}), 
        choices=gameTypes, label="Game Types",
        initial=['PR', 'R', 'P', 'A'])
    divide_by_season = forms.BooleanField(label="Divide By Season",
        widget=forms.CheckboxInput(attrs={'class': 'game-type-checkbox'}))
    date_start = forms.DateField(label="Start Date",
        widget=forms.DateInput(attrs={'class': 'form-control input-sm datepicker'}))
    date_end = forms.DateField(label="End Date",
        widget=forms.DateInput(attrs={'class': 'form-control input-sm datepicker'}))
