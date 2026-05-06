from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime

# Importing all models from models.py

from .models import Organizer, Student, Event, Registration, Feedback

# Importing serializers

from .serializers import (
    OrganizerSerializer,
    StudentSerializer,
    EventSerializer,
    RegistrationSerializer,
    FeedbackSerializer
)

# This ViewSet handles all operations related to Organizer
class OrganizerViewSet(viewsets.ModelViewSet):

    # Fetching all Organizer records from database
    queryset = Organizer.objects.all()

    # Connecting this ViewSet with OrganizerSerializer
    serializer_class = OrganizerSerializer


# Handles CRUD operations for Student model
class StudentViewSet(viewsets.ModelViewSet):

    # Getting all Student records
    queryset = Student.objects.all()

    # Using StudentSerializer to convert data
    serializer_class = StudentSerializer


# Handles all operations related to Event model
class EventViewSet(viewsets.ModelViewSet):

   
    queryset = Event.objects.all()

    # Using EventSerializer for data conversion
    serializer_class = EventSerializer

# Manages student registrations for events
class RegistrationViewSet(viewsets.ModelViewSet):

    # select_related is used to fetch related student and event data efficiently
    queryset = Registration.objects.select_related("student", "event").all()

    # Serializer used for Registration model
    serializer_class = RegistrationSerializer


# Manages feedback given by students for events
class FeedbackViewSet(viewsets.ModelViewSet):

    # Fetching feedback along with related student and event in single query
    queryset = Feedback.objects.select_related("student", "event").all()

    # Serializer for Feedback model
    serializer_class = FeedbackSerializer



class EventsByOrganizerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    # Using EventSerializer to return event data
    serializer_class = EventSerializer

    # Overriding get_queryset method to filter events dynamically
    def get_queryset(self):

        # Getting organizer_id from URL parameters
        organizer_id = self.kwargs.get("organizer_id")

        # If organizer does not exist, it returns 404 automatically
        organizer = get_object_or_404(
            Organizer,
            organizer_id=organizer_id
        )

        # select_related improves performance by reducing database queries
        return organizer.events.select_related("organizer").all()

from functools import wraps

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('student_email'):
            messages.warning(request, "Please log in to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_student_from_session(request):
    email = request.session.get('student_email')
    return Student.objects.filter(email=email).first() if email else None

def home_view(request):
    return render(request, "home.html", {"student": get_student_from_session(request)})

@custom_login_required
def event_list_view(request):
    events = Event.objects.all()
    email = request.session.get('student_email')
    student_obj = Student.objects.filter(email=email).first() if email else None
    return render(request, "events.html", {"events": events, "student": student_obj})

@custom_login_required
def post_event_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        city = request.POST.get("location")  # Location mapped to city
        event_date = request.POST.get("event_date")  # e.g., '2024-12-10'
        event_time = request.POST.get("event_time")  # e.g., '10:00'

        start_date = None
        if event_date:
            try:
                # Combine date and time if time is provided, otherwise just date
                if event_time:
                    date_str = f"{event_date} {event_time}"
                    start_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()
                else:
                    start_date = datetime.strptime(event_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                start_date = None

        print("FILES:", request.FILES)
        image = request.FILES.get("image")

        event = Event(
            title=title,
            category=category,
            city=city,
            start_date=start_date,
            status="Upcoming"
        )
        if image:
            event.image = image
        event.save()
        return redirect("event_list")
        
    return render(request, "post-event.html", {"student": get_student_from_session(request)})

def event_details_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    student = get_student_from_session(request)
    feedbacks = event.feedbacks.select_related('student').order_by('-created_at')
    
    is_registered = False
    if student:
        is_registered = Registration.objects.filter(student=student, event=event).exists()
        
    return render(request, "event_details.html", {
        "event": event, 
        "student": student,
        "feedbacks": feedbacks,
        "is_registered": is_registered
    })

def event_registration_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "POST":
        name        = request.POST.get("name", "").strip()
        email       = request.POST.get("email", "").strip()
        roll_number = request.POST.get("student_id", "").strip()
        request.session['student_email'] = email

        # --- Validation ---
        if not name or not email or not roll_number:
            messages.error(request, "All fields are required. Please fill in your name, email and roll number.")
            return render(request, "event_registration.html", {"event": event, "student": get_student_from_session(request)})

        # --- Get or create student by email ---
        student = Student.objects.filter(email=email).first()
        if student:
            # Update name / roll number if they changed
            student.name        = name
            student.roll_number = roll_number
            student.save()
        else:
            student = Student.objects.create(
                name=name,
                email=email,
                roll_number=roll_number,
            )

        # --- Duplicate registration check ---
        already_registered = Registration.objects.filter(student=student, event=event).exists()
        if already_registered:
            messages.warning(request, f"You are already registered for '{event.title}'. No duplicate registration created.")
            return render(request, "event_registration.html", {"event": event, "student": get_student_from_session(request)})

        # --- Create the registration ---
        Registration.objects.create(
            student=student,
            event=event,
            status="Registered"
        )

        messages.success(request, f"Successfully registered for '{event.title}'! We'll see you there.")
        return redirect("event_list")

    return render(request, "event_registration.html", {"event": event, "student": get_student_from_session(request)})


@custom_login_required
def feedback_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    student = get_student_from_session(request)
    
    # Enforce registration restriction
    is_registered = Registration.objects.filter(student=student, event=event).exists()
    if not is_registered:
        messages.error(request, "You can only leave feedback for events you are registered for.")
        return redirect("event_details", event_id=event.event_id)
    
    # Check if this student already gave feedback for this event
    feedback = Feedback.objects.filter(student=student, event=event).first()

    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comments = request.POST.get("comments", "").strip()

        if feedback:
            # Update existing feedback
            feedback.rating = rating
            feedback.comments = comments
            feedback.save()
            messages.success(request, "Feedback updated successfully!")
        else:
            # Create new feedback
            Feedback.objects.create(
                student=student,
                event=event,
                rating=rating,
                comments=comments
            )
            messages.success(request, "Thank you! Your feedback has been submitted successfully!")

        return redirect("dashboard")

    return render(request, "feedback.html", {"event": event, "student": student, "feedback": feedback})

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        roll_number = request.POST.get("roll_number", "").strip()
        password = request.POST.get("password", "").strip()

        if not name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "signup.html")

        if Student.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, "signup.html")

        Student.objects.create(
            name=name,
            email=email,
            roll_number=roll_number,
            password=password
        )
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate against Student model
        student = Student.objects.filter(email=email, password=password).first()

        if student is not None:
            # Set session for student logic
            request.session['student_email'] = student.email
            
            messages.success(request, f"Welcome back, {student.name}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")

def logout_view(request):
    request.session.pop('student_email', None)
    return render(request, "logout.html", {})

@custom_login_required
def dashboard_view(request):
    email = request.session.get('student_email')

    registrations = []
    student_obj = None
    if email:
        student_obj = Student.objects.filter(email=email).first()
        if student_obj:
            registrations = Registration.objects.filter(student=student_obj).select_related("event")

    return render(request, "dashboard.html", {
        "student": student_obj,
        "registrations": registrations
    })





