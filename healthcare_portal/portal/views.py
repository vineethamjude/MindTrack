from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Answer, Appointment, CustomUser, Question
from .util import determine_sentiment


def logout_view(request):
    # Perform the logout operation
    logout(request)

    # Check the referrer URL
    referer = request.META.get("HTTP_REFERER", "")

    # Redirect based on the referrer
    if "/patient" in referer:
        return redirect(
            reverse("patient_view"),
        )
    elif "/doctor" in referer:
        return redirect(
            reverse("doctor_dashboard"),
        )
    else:
        return redirect(reverse("admin:index"))


@login_required
def patient_view(request):
    # check if the logged in user is a patient. If not log out and redirect to the login page
    if request.user.user_type != "PATIENT":
        print("You must be a patient")
        return redirect("logout")

    patient_wants_to_consult = False

    if request.method == "POST":
        print(f"{request.POST.get('page_one')}, {type(request.POST.get('page_one'))}")
        cumulative_sentiment = 0
        first_step_completed = True if request.POST.get("page_one") == "true" else False
        if first_step_completed:
            answers_ids = []
            answers: list[Answer] = []  # Use this list to keep track of all the answers
            for question in Question.objects.all():
                answer_text = request.POST.get(str(question.id))
                print(f"Q: {question.text} = A-{answer_text}")
                if (
                    question.text
                    == 'Do you want to consult a doctor? Enter "yes" or "no".'
                    or question.text == "Calculated Sentiment Average Score (-1 to 1)"
                ):
                    # the consult question is present in page one but it's hidden
                    # we do not want to save it as the question is only shown in page 2
                    continue

                answer = Answer.objects.create(
                    patient=request.user, question=question, answer=answer_text
                )
                answers_ids.append(answer.id)
                answers.append(answer)  # Add the created answer to the list
                # calculate sentiment from question and answer
                sentiment_value = determine_sentiment(
                    answer.question.text, answer.answer
                )
                print(
                    f"Question: {answer.question.text}\nAnswer: {answer.answer}\nCalculated sentiment: {sentiment_value}\n\n"
                )
                cumulative_sentiment += sentiment_value

            average_sentiment = cumulative_sentiment / len(answers)
            request.session["answers_ids"] = answers_ids
            request.session["average_sentiment"] = average_sentiment

            return render(
                request,
                "patient_after_submission.html",
                {
                    "questions": Question.objects.all(),
                    "associated_appointments": Appointment.objects.filter(
                        patient=request.user, appointment_completed=False
                    ),
                    "average_sentiment": round(average_sentiment, 2),
                },
            )
        # All mental health questions have been recorded and now the patient is asked if
        # they need an appointment.
        else:
            # get completed answers from the previous page from the session data
            answers_ids_from_session = request.session.get("answers_ids", [])
            answers = list(Answer.objects.filter(id__in=answers_ids_from_session))
            print(answers)
            print(type(answers))
            print(type(answers[0]))
            average_sentiment = request.session.get("average_sentiment", 0)
            print(f"Average sentiment: {average_sentiment}")

            if average_sentiment < -0.5:
                print(f"Average sentiment is very negative: {average_sentiment}")
                # Highly negative average sentiment detected
                # Action needed, for example, prioritizing consultation, logging, etc.

            for question in Question.objects.all():
                answer_text = request.POST.get(str(question.id))
                print(f"Q: {question.text} = A-{answer_text}")
                if (
                    question.text
                    == 'Do you want to consult a doctor? Enter "yes" or "no".'
                    and answer_text.lower() == "yes"
                ):
                    print("Patient wants to consult")
                    patient_wants_to_consult = True

                    answer = Answer.objects.create(
                        patient=request.user, question=question, answer=answer_text
                    )
                    answers.append(answer)  # Add the created answer to the list

            # Save calculated sentiment score as a question answer
            score_question, _ = Question.objects.get_or_create(
                text="Calculated Sentiment Average Score (-1 to 1)"
            )
            answers.append(
                Answer.objects.create(
                    patient=request.user,
                    question=score_question,
                    answer=str(average_sentiment),
                )
            )

            first_available_doctor_object = CustomUser.objects.filter(
                user_type="DOCTOR", availability=True
            ).first()

            if first_available_doctor_object:
                first_available_doctor_message = f"The first available doctor is Dr. {first_available_doctor_object.first_name}. We have shared your details with the doctor."
                sub_text = "Please contact 0471-6598413 to schedule an appointment."
            else:
                first_available_doctor_message = "Sorry. No doctors available at this time. Please contact 0471-6598321 to discuss alternatives."
                sub_text = ""

            print(f"First available doctor: {first_available_doctor_message}")

            if first_available_doctor_object and patient_wants_to_consult:
                # Create the appointment
                appointment = Appointment.objects.create(
                    patient=request.user, doctor=first_available_doctor_object
                )
                appointment.associated_answers.set(
                    answers
                )  # Link the answers to the appointment
                appointment.save()

                # If you want to enable the functionality where a doctor becomes unavailable on an appointment booking
                # this could be a config
                first_available_doctor_object.availability = (
                    False  # mark the doctor as no longer available
                )
                first_available_doctor_object.save()

            # cleanup session data
            del request.session["answers_ids"]
            del request.session["average_sentiment"]
            return render(
                request,
                "thank_you.html",
                {
                    "want_to_consult": patient_wants_to_consult,
                    "first_available_doctor": first_available_doctor_message,
                    "sub_text": sub_text,
                },
            )

    return render(
        request,
        "patient_view.html",
        {
            "questions": Question.objects.all(),
            "associated_appointments": Appointment.objects.filter(
                patient=request.user, appointment_completed=False
            ),
        },
    )


@login_required
def doctor_dashboard(request):
    # check if the logged in user is a doctor. If not log out and redirect to the login page
    if request.user.user_type != "DOCTOR":
        print("You must be a doctor")
        return redirect("logout")

    appointments = Appointment.objects.filter(
        doctor=request.user, appointment_completed=False
    )
    print(appointments)
    return render(request, "doctor_dashboard.html", {"appointments": appointments})


@login_required
def set_availability(request):
    if request.method == "POST":
        # Check if the user is a doctor first
        if request.user.user_type == "DOCTOR":
            request.user.availability = not request.user.availability
            request.user.save()
    return redirect("doctor_dashboard")


from django.shortcuts import redirect, render


def register(request):
    if request.method == "POST":
        # Extract data from the form
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        age = request.POST.get("age")
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type", "PATIENT")

        # Create the patient
        user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            age=age,
            user_type=user_type,
            username=username,
            password=password,
        )
        user.save()
        return redirect("/accounts/login/?next=/patient/")

    return render(request, "register.html")


from django.shortcuts import get_object_or_404, redirect

from .models import Appointment


def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.appointment_completed = True
    appointment.save()
    return redirect("doctor_dashboard")
