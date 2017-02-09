from django.contrib.auth import logout as user_logout
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from stravalib import Client

from strava_club_challenge.models import Challenge
from stravauth.models import StravaToken


def get_token(user):
    return StravaToken.objects.get(user=user).token


def get_progress(user, challenge):
    total_distance = 0
    for activity in Client(get_token(user)).get_activities(
            after=challenge.start_date,
            before=challenge.end_date
    ):
        if activity.type == "Run":
            # activity distance is given in kilometers.
            total_distance += float(activity.distance) / 1000.0
    return int(round(total_distance / challenge.goal_distance * 100.0))


def index(request):
    if not request.user.is_authenticated():
        return render(request, "index.xhtml")
    else:
        client = Client(get_token(request.user))
        club_challenges = []
        for club in client.get_athlete_clubs():
            soon_ending_challenges = Challenge.objects.order_by('end_date').filter(club=club.name)[:3]
            progresses = [get_progress(request.user, challenge) for challenge in soon_ending_challenges]
            club_challenges.append((club, list(zip(soon_ending_challenges, progresses))))
        context = {"clubs": sorted(club_challenges, key=lambda x: len(x[1]), reverse=True)}
        return render(request, "index.xhtml", context=context)


def logout(request):
    user_logout(request)
    return render(request, "index.xhtml")


def challenge_list(request):
    context = {}
    if request.user.is_authenticated():
        context["my_challenges"] = Challenge.objects.filter(participant=StravaToken.objects.get(user=request.user))
        context["my_challenges"] = zip(context["my_challenges"], [get_progress(request.user, challenge) for challenge in
                                                                  context["my_challenges"]])
    return render(request, "challenge/list.xhtml", context=context)


from .forms import ChallengeForm


def challenge_create(request):
    challenge_form = ChallengeForm(initial={'participant': StravaToken.objects.get(user=request.user).id})
    if request.method == "POST":
        challenge_form = ChallengeForm(request.POST)
        if challenge_form.is_valid():
            # add message
            challenge_form.save()
            return HttpResponseRedirect(reverse_lazy('challenge_create'))
    return render(request, "challenge/create.xhtml", context={"challenge_form": challenge_form})


def challenge_page(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        raise Http404('Challenge does not exist')
    return render(request, 'challenge/challenge.xhtml', context={"challenge": challenge})
