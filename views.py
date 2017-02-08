from datetime import datetime

from django.contrib.auth import logout as user_logout
from django.shortcuts import render
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
            # activity distance is given in meters.
            total_distance += float(activity.distance)
    print(total_distance)
    return total_distance / challenge.goal_distance


def index(request):
    return render(request, "index.xhtml")


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


def challenge_create(request):
    new_c = Challenge()
    # in metres
    new_c.goal_distance = 200
    new_c.start_date = datetime.strptime("2017-01-01", "%Y-%m-%d")
    new_c.end_date = datetime.strptime("2018-01-01", "%Y-%m-%d")
    new_c.participant = StravaToken.objects.get(user=request.user)
    new_c.save()
    return render(request, "challenge/create.xhtml")
