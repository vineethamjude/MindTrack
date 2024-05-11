from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPES = (
        ("ADMIN", "Admin"),
        ("DOCTOR", "Doctor"),
        ("PATIENT", "Patient"),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default="PATIENT")
    age = models.IntegerField(null=True, blank=True)
    # Add the availability field with a default of False
    availability = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If the user is not of type 'DOCTOR', ensure availability is always False
        if self.user_type != "DOCTOR":
            self.availability = False
        super().save(*args, **kwargs)


class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class Answer(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return f"Answer by {self.patient.username} to '{self.question.text}' is {self.answer}"


class Appointment(models.Model):
    patient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="patient_appointments"
    )
    doctor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="doctor_appointments"
    )
    associated_answers = models.ManyToManyField(Answer)
    appointment_completed = models.BooleanField(default=False)

    def clean(self):
        # Check that patient user_type is PATIENT
        if self.patient.user_type != "PATIENT":
            raise ValidationError({"patient": "The selected user is not a patient."})

        # Check that doctor user_type is DOCTOR
        if self.doctor.user_type != "DOCTOR":
            raise ValidationError({"doctor": "The selected user is not a doctor."})

    def save(self, *args, **kwargs):
        # Run the clean method to validate our model's fields
        self.clean()

        super(Appointment, self).save(*args, **kwargs)

    def __str__(self):
        return f"Appointment for {self.patient.first_name} with Dr. {self.doctor.first_name}"
