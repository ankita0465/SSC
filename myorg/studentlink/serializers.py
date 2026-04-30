# Importing serializers module from Django REST Framework
from rest_framework import serializers

# Importing all required models
from .models import Organizer, Student, Event, Registration, Feedback

# Organizer Serializer
class OrganizerSerializer(serializers.ModelSerializer):

    class Meta:
        # Connecting this serializer with Organizer model
        model = Organizer

        # These are the fields that will be shown in API response

        fields = [
            "organizer_id",
            "name",
            "email",
            "phone",
            "organization_type",
            "verified_status",
            "created_at",
            "update_at"
        ]

# Student Serializer

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        # Linking with Student model
        model = Student

        # Only selected fields are included
        # Password field is excluded for security
        fields = [
            "student_id",
            "name",
            "email",
            "city",
            "created_at",
            "update_at"
        ]

# Event Serializer
# This serializer converts Event model data into JSON
class EventSerializer(serializers.ModelSerializer):

    class Meta:
        # Linking with Event model
        model = Event

        # Fields that will be visible in API
        fields = [
            "event_id",
            "title",
            "category",
            "city",
            "start_date",
            "status",
            "created_at",
            "updated_at"
        ]

# Registration Serializer

class RegistrationSerializer(serializers.ModelSerializer):

    # Showing full student details instead of only student_id
    student = StudentSerializer(read_only=True)

    event = EventSerializer(read_only=True)

    class Meta:
      
        model = Registration

        # Fields included in API response
        fields = [
            "registration_id",
            "student",
            "event",
            "registration_date",
            "created_at",
            "updated_at",
            "status"
        ]

# Feedback Serializer

class FeedbackSerializer(serializers.ModelSerializer):


    student = StudentSerializer(read_only=True)


    event = EventSerializer(read_only=True)

    class Meta:
      
        model = Feedback

        # Fields that will appear in API
        fields = [
            "feedback_id",
            "student",
            "event",
            "rating",
            "comments",
            "created_at",
            "updated_at"
        ]

