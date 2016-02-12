from django import forms
from team.models import Team
from team.models import Venue
import constants

class GamesFilter(forms.Form):
    a = (
        (20152016, '2015 - 2016'),
        (20142015, '2014 - 2015')
    )
    teams = forms.MultipleChoiceField(label='Teams', choices=constants.teamNames)
    
    seasons = forms.MultipleChoiceField(label='Seasons', choices=a)
    
    status = forms.ChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Status', choices=constants.gameStates)
    
    venues = forms.ModelChoiceField(widget=forms.Select(attrs={'class' : 'form-control input-sm'}), 
        label='Venue', queryset=Venue.objects.all().order_by('name'))
    
    session = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class' : 'session-checkbox'}), 
        choices=constants.gameTypes)