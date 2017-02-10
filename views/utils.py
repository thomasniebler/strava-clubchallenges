from django.utils import timezone
from stravalib import Client
from stravauth.models import StravaToken

from strava_club_challenge.models import Participation


def get_token(user):
    """
    returns the StravaToken object for a user.
    :param user:
    :return:
    """
    return StravaToken.objects.get(user=user)


def get_progress(user, challenge):
    """
    Returns the challenge progress for a given user in rounded percent.
    :param user:
    :param challenge:
    :return:
    """
    total_distance = 0
    for activity in Client(get_token(user).token).get_activities(
            after=challenge.start_date,
            before=challenge.end_date
    ):
        if activity.type == "Run":
            # activity distance is given in kilometers.
            total_distance += float(activity.distance) / 1000.0
    return int(round(total_distance / challenge.goal_distance * 100.0))


def logged_in_user_participates_in(request, challenge):
    return len(Participation.objects.filter(challenge=challenge, participant=get_token(request.user))) > 0


def can_join_challenge(request, challenge):
    return not logged_in_user_participates_in(request, challenge) \
           and challenge.start_date < timezone.now() \
           and challenge.end_date > timezone.now()
