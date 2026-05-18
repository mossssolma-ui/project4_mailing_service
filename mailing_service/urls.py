from django.urls import path
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers

from mailing_service.apps import MailingServiceConfig
from . import views

app_name = MailingServiceConfig.name

urlpatterns = [
    path("",
         vary_on_headers('Cookie')(
             cache_control(max_age=300, private=True)(
                 views.HomeView.as_view()
             )
         ),
         name="home"),

    path("recipient/", views.RecipientList.as_view(), name="recipient_list"),
    path("recipient/<int:pk>/details/", views.RecipientDetail.as_view(), name="recipient_details"),
    path("recipient/create/", views.RecipientCreate.as_view(), name="recipient_create"),
    path("recipient/<int:pk>/update/", views.RecipientUpdate.as_view(), name="recipient_update"),
    path("recipient/<int:pk>/delete/", views.RecipientDelete.as_view(), name="recipient_delete"),

    path("message/", views.MessageList.as_view(), name="message_list"),
    path("message/<int:pk>/details/", views.MessageDetail.as_view(), name="message_details"),
    path("message/create/", views.MessageCreate.as_view(), name="message_create"),
    path("message/<int:pk>/update/", views.MessageUpdate.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", views.MessageDelete.as_view(), name="message_delete"),

    path("distribution/", views.DistributionList.as_view(), name="distribution_list"),
    path("distribution/<int:pk>/details/", views.DistributionDetail.as_view(), name="distribution_details"),
    path("distribution/create/", views.DistributionCreate.as_view(), name="distribution_create"),
    path("distribution/<int:pk>/update/", views.DistributionUpdate.as_view(), name="distribution_update"),
    path("distribution/<int:pk>/delete/", views.DistributionDelete.as_view(), name="distribution_delete"),
    path("distribution/<int:pk>/disable/", views.DistributionDisableView.as_view(), name="distribution_disable"),

    path("attempts/", views.AttemptList.as_view(), name="attempt_list"),
]
