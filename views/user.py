from django.http import HttpResponseNotFound
from django.shortcuts import render
from stravauth.models import StravaToken
from .utils import get_athlete_data


def user_page(request, user_id):
    users = list(filter(lambda x: x.id == int(user_id), [get_athlete_data(blob.user) for blob in StravaToken.objects.all()]))
    if len(users) > 0:
        context = {"user": users[0]}
    else:
        return HttpResponseNotFound()
    return render(request, "user/user_page.xhtml", context=context)