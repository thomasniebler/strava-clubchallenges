from django.contrib.auth import logout as user_logout
from django.shortcuts import render
from django.utils import timezone
from stravalib import Client

from strava_club_challenge.models import Challenge
from .utils import get_token, get_progress, logged_in_user_participates_in


def index(request):
    if not request.user.is_authenticated:
        return render(request, "index.xhtml")
    else:
        client = Client(get_token(request.user).token)
        club_challenges = []
        for club in client.get_athlete_clubs():
            club.clean_name = "".join(character for character in club.name.lower()
                                      if ord(character) >= 97 and ord(character) <= 122)
            soon_ending_challenges = Challenge.objects.order_by('end_date').filter(
                start_date__lt=timezone.now()).filter(club=club.name)[:3]
            progresses = [get_progress(request.user, challenge) for challenge in soon_ending_challenges]
            participates = [logged_in_user_participates_in(request, challenge) for challenge in soon_ending_challenges]
            club_challenges.append((club, list(zip(soon_ending_challenges, progresses, participates))))
        context = {"clubs": sorted(club_challenges, key=lambda x: len(x[1]), reverse=True)}
        return render(request, "index.xhtml", context=context)


def logout(request):
    user_logout(request)
    return render(request, "index.xhtml")
