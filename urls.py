from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls.base import reverse_lazy

from stravauth.views import StravaAuth
from . import views

urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  url(r'^login/$', StravaAuth.as_view(url=reverse_lazy("index")), kwargs={"approval_prompt": "force"},
                      name="login"),
                  url(r'^logout/$', views.logout, name='logout'),

                  url(r'^challenge/list$', views.challenge_list, name='challenge_list'),
                  url(r'^challenge/create$', views.challenge_create, name='challenge_create'),
                  url(r'^challenge/id/(?P<challenge_id>[0-9]+)$', views.challenge_page, name='challenge_page'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
