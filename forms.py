from django import forms

from strava_club_challenge.models import Challenge


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['goal_distance', 'start_date', 'end_date', 'club']
        widgets = {'goal_distance': forms.NumberInput(),
                   'start_date': forms.DateInput(),
                   'end_date': forms.DateInput(),
                   'club': forms.TextInput()}
