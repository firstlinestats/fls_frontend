from django import forms
from player.models import Player
from playbyplay.models import PlayerGameStats
from player.constants import skaterPositions
from playbyplay.constants import homeAway


class PlayerStatsFilter(forms.Form):
    home_or_away = forms.Select(label='Home/Away Situation',
        choices=homeAway)
    toi = forms.IntegerField(min_value=0)
    position = forms.MultipleChoiceField(label='Position',
        choices=skaterPositions)
    seasons = forms.ModelChoiceField(
        widget=forms.SelectMultiple(
            attrs={'class' : 'form-control input-sm'}), 
        label='Specify Seasons',
        queryset=Game.objects.values_list('season', flat=True)\
            .distinct(), empty_label=None)
    gameType = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={'class' : 'game-type-checkbox'}), 
        choices=constants.gameTypes,
        initial=['PR', 'R', 'P', 'A'])
    divideBySeason = forms.BooleanField(label="Divide By Season")
    dateStart = forms.DateField()
    dateEnd = forms.DateField()
