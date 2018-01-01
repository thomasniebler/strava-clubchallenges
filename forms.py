from django import forms

from strava_club_challenge.models import Challenge


class ChallengeForm(forms.ModelForm):
    tmp = ["Hund"]

    class Meta:
        model = Challenge
        fields = ['goal_distance', 'start_date', 'end_date', 'club']
        widgets = {'goal_distance': forms.NumberInput(attrs={"placeholder": "Goal Distance in km"}),
                   'start_date': forms.DateInput(
                       attrs={"type": "date", "placeholder": "Start Date", "class": "datepicker"}),
                   'end_date': forms.DateInput(
                       attrs={"type": "date", "placeholder": "End Date", "class": "datepicker"}),
                   'club': forms.Select(attrs={"placeholder": "Club"}, choices=[("Hund", "Hund")])}
