from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from stravauth.models import StravaToken

from strava_club_challenge.forms import ChallengeForm
from strava_club_challenge.models import Challenge, Participation
from .utils import get_progress, logged_in_user_participates_in


def challenge_list(request):
    context = {}
    if request.user.is_authenticated():
        context["my_challenges"] = Challenge.objects.filter(
            participation__participant=StravaToken.objects.get(user=request.user))
        context["my_challenges"] = zip(context["my_challenges"], [get_progress(request.user, challenge) for challenge in
                                                                  context["my_challenges"]])
        context["other_challenges"] = Challenge.objects.exclude(
            participation__participant=StravaToken.objects.get(user=request.user))
    return render(request, "challenge/list.xhtml", context=context)


def challenge_join(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        if not logged_in_user_participates_in(request, challenge):
            participation = Participation()
            participation.challenge = challenge
            participation.participant = StravaToken.objects.get(user=request.user)
            participation.save()
        return HttpResponseRedirect(reverse("challenge_page", kwargs={"challenge_id": challenge_id}))
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    return render(request, 'challenge/challenge.xhtml', context={"challenge": challenge})


def challenge_leave(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        participation = Participation.objects.filter(challenge=challenge,
                                                     participant=StravaToken.objects.get(user=request.user))
        participation.delete()
        return HttpResponseRedirect(reverse("challenge_page", kwargs={"challenge_id": challenge_id}))
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    return render(request, 'challenge/challenge.xhtml', context={"challenge": challenge})


def challenge_create(request):
    challenge_form = ChallengeForm()  # initial={'club': list(Client(get_token(request.user).token).get_athlete_clubs())}
    if request.method == "POST":
        challenge_form = ChallengeForm(request.POST)
        if challenge_form.is_valid():
            # add message
            challenge_form.save()
            return HttpResponseRedirect(reverse_lazy('challenge_create'))
    return render(request, "challenge/create.xhtml", context={"challenge_form": challenge_form})


def challenge_page(request, challenge_id):
    context = {}
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        participants = list(Participation.objects.all())
        context["challenge"] = challenge
        context["participants"] = participants
    except Challenge.DoesNotExist:
        raise Http404('Challenge does not exist')
    return render(request, 'challenge/challenge.xhtml', context=context)
