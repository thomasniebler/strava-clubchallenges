from django.contrib import messages
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from stravalib.client import Client
from stravauth.models import StravaToken

from strava_club_challenge.forms import ChallengeForm
from strava_club_challenge.models import Challenge, Participation
from strava_club_challenge.views.utils import get_token
from .utils import get_progress, can_join_challenge


def challenge_list(request, past_challenges=False, ):
    context = {}
    if request.user.is_authenticated():
        challenges = Challenge.objects.filter(start_date__lt=timezone.now()).filter(
            participation__participant=StravaToken.objects.get(user=request.user))
        progresses = [get_progress(request.user, challenge) for challenge in challenges]
        joinable = [chall.end_date > timezone.now() for chall in challenges]
        context["my_challenges"] = zip(challenges, progresses, joinable)
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
            messages.add_message(request, messages.SUCCESS, "You joined this challenge.")
        else:
            messages.add_message(request, messages.ERROR, "You cannot join this challenge.")
        return HttpResponseRedirect(reverse("challenge_page", kwargs={"challenge_id": challenge_id}))
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    return challenge_page(request, challenge_id)


def challenge_leave(request, challenge_id):
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        participation = Participation.objects.filter(challenge=challenge,
                                                     participant=StravaToken.objects.get(user=request.user))
        participation.delete()
        messages.add_message(request, messages.SUCCESS, "You left this challenge.")
        return HttpResponseRedirect(reverse("challenge_page", kwargs={"challenge_id": challenge_id}))
    except Challenge.DoesNotExist:
        raise Http404("Challenge does not exist")
    return challenge_page(request, challenge_id)


def challenge_create(request):
    challenge_form = ChallengeForm()  # initial={'club': list(Client(get_token(request.user).token).get_athlete_clubs())}
    club_choices = [(club.name, club.name) for club in Client(get_token(request.user).token).get_athlete_clubs()]
    challenge_form.fields["club"].choices = club_choices
    challenge_form._meta.widgets["club"].choices = club_choices
    if request.method == "POST":
        challenge_form = ChallengeForm(request.POST)
        if challenge_form.is_valid():
            # add message
            challenge_form.save()
            messages.add_message(request, messages.SUCCESS, "You successfully created a challenge!")
            return HttpResponseRedirect(reverse('challenge_list'))
    return render(request, "challenge/create.xhtml", context={"challenge_form": challenge_form})


def challenge_page(request, challenge_id):
    context = {}
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        participants = list(Participation.objects.filter(challenge=challenge))
        context["joinable"] = challenge.end_date > timezone.now()
        context["participates"] = request.user in [part.participant.user for part in participants]
        context["challenge"] = challenge
        progress = [get_progress(participant.participant.user, challenge) for participant in participants]
        completed = [prog >= 100 for prog in progress]
        context["participants"] = sorted(zip(participants, progress, completed), key=lambda x: x[1])
    except Challenge.DoesNotExist:
        raise Http404('Challenge does not exist')
    return render(request, 'challenge/challenge.xhtml', context=context)
