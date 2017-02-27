from django import template

from strava_club_challenge.views import utils

register = template.Library()


@register.inclusion_tag('tags/user.xhtml')
def user_avatar(user):
    return {"user": utils.get_athlete_data(user)}
