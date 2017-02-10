from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from stravauth.models import StravaToken

from strava_club_challenge.forms import ChallengeForm
from strava_club_challenge.models import Challenge, Participation
from .utils import get_progress, can_join_challenge


def challenge_list(request):
    context = {}
    if request.user.is_authenticated():
        challenges = Challenge.objects.filter(start_date__lt=timezone.now()).filter(
            participation__participant=StravaToken.objects.get(user=request.user))
        progresses = [get_progress(request.user, challenge) for challenge in challenges]
        context["my_challenges"] = zip(challenges, progresses)
        context["other_challenges"] = Challenge.objects.exclude(
            participation__participant=StravaToken.objects.get(user=request.user))
    return render(request, "challenge/list.xhtml", context=context)


def challenge_join(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        if can_join_challenge(request, challenge):
            participation = Participation()
            participation.challenge = challenge
            participation.participant = StravaToken.objects.get(user=request.user)
            participation.save()
        else:
            print(
                "User tried to join a challenge that hasn't started or is already over or that he is already taking part in")
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
            return HttpResponseRedirect(reverse('challenge_list'))
    return render(request, "challenge/create.xhtml", context={"challenge_form": challenge_form})


def challenge_page(request, challenge_id):
    context = {}
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        participants = list(Participation.objects.filter(challenge=challenge))
        context["challenge"] = challenge
        context["participants"] = participants
    except Challenge.DoesNotExist:
        raise Http404('Challenge does not exist')
    return render(request, 'challenge/challenge.xhtml', context=context)
