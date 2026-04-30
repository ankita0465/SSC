from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizerViewSet, StudentViewSet, EventViewSet, RegistrationViewSet, FeedbackViewSet,
    EventsByOrganizerViewSet,
    home_view, event_list_view, post_event_view, event_details_view, event_registration_view,
    feedback_view, dashboard_view, login_view, signup_view, logout_view
)

# Creating a router object
router = DefaultRouter()

# Second argument = ViewSet class
router.register("organizers", OrganizerViewSet)
router.register("students", StudentViewSet)
router.register("events", EventViewSet)
router.register("registrations", RegistrationViewSet)
router.register("feedbacks", FeedbackViewSet)
router.register("organizer-events", EventsByOrganizerViewSet, basename="organizer-events")


urlpatterns = [
    path("", home_view, name="home"),
    path("index/", home_view, name="home_index"),
    path("event-list/", event_list_view, name="event_list"),
    path("post-event/", post_event_view, name="post_event"),
    path("event/<int:event_id>/", event_details_view, name="event_details"),
    path("event/<int:event_id>/register/", event_registration_view, name="event_registration"),
    path("event/<int:event_id>/feedback/", feedback_view, name="event_feedback"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),

    # THEN router LAST
    path("api/", include(router.urls)),

      
]
