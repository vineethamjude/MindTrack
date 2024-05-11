from django.urls import path

from . import views

urlpatterns = [
    path("patient/", views.patient_view, name="patient_view"),
    path("doctor/", views.doctor_dashboard, name="doctor_dashboard"),
    path("set_availability/", views.set_availability, name="set_availability"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "complete_appointment/<int:appointment_id>/",
        views.complete_appointment,
        name="complete_appointment",
    ),
]
