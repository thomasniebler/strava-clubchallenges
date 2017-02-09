from django.forms import ModelForm, HiddenInput

from .models import Challenge


class ChallengeForm(ModelForm):
    class Meta:
        model = Challenge
        fields = ['goal_distance', 'start_date', 'end_date', 'club', 'participant']
        widgets = {'participant': HiddenInput()}
