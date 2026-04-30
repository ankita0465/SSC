# Importing models module from Django to define database models
from django.db import models

class Organizer(models.Model):

    # Primary Key (unique identifier for each organizer)
    organizer_id = models.IntegerField(primary_key=True)

    # Organizer name
    name = models.CharField(max_length=100, default="Unknown Organizer")

    # Organizer email
    email = models.CharField(max_length=100,default="unknown@example.com", unique=True, null=False, blank=False)

    # Organizer password (stored as text)
    password = models.CharField(max_length=100, default="password")

    # Contact phone number
    phone = models.CharField(max_length=15, default="0000000000")

    # Type of organization (e.g., College, Company, NGO)
    organization_type = models.CharField(max_length=50, default="General")

    # Verification status (e.g., Verified / Pending)
    verified_status = models.CharField(max_length=20, default="Pending")

    # Date when record was created
    created_at = models.DateField( auto_now_add=True, null=True, blank=True) 

    # Date when record was last updated
    update_at = models.DateField(auto_now=True, null=True, blank=True)

    # Meta class for extra configuration
    class Meta:
        db_table = "organizer"

    def __str__(self):
        return self.name


# Student Model
class Student(models.Model):

    # Auto-increment primary key
    student_id = models.AutoField(primary_key=True)

    # Student name
    name = models.CharField(max_length=100, default='Student')

    # Student email
    email = models.CharField(max_length=100, unique=True)

    # Student roll number 
    roll_number = models.CharField(max_length=50, default='', blank=True)

    # Student password
    password = models.CharField(max_length=100, default='')

    # Student city
    city = models.CharField(max_length=50, default='Unknown')

    # Record creation date (auto-filled)
    created_at = models.DateField(auto_now_add=True, null=True)

    # Record update date (auto-filled)
    update_at = models.DateField(auto_now=True, null=True)

    class Meta:
        # Custom table name in database
        db_table = "student"

    # How student object will display
    def __str__(self):
        return self.name


# Event Model
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)  
    title = models.CharField(max_length=100, default='Untitled Event')
    category = models.CharField(max_length=50, default='General')
    city = models.CharField(max_length=50, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Upcoming')
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True,  null=True)

    class Meta:
        db_table = "event"

    def __str__(self):
        return self.title


# Registration Model
class Registration(models.Model):

    # Auto-increment primary key
    registration_id = models.AutoField(primary_key=True)

    # ForeignKey to Student
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        db_column="student_id",
        related_name="registrations"
    )

    # ForeignKey to Event
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        db_column="event_id",
        related_name="registrations"
    )

    # Date when student registered 
    registration_date = models.DateField(auto_now_add=True, null=True)

    # Record creation date
    created_at = models.DateField(auto_now_add=True, null=True)

    # Record update date
    updated_at = models.DateField(auto_now=True, null=True)

    # Registration status
    status = models.CharField(max_length=20, default='Registered')

    class Meta:
        # Custom table name
        db_table = "registration"
        # Prevent same student registering twice for same event
        unique_together = ('student', 'event')


# Feedback Model
class Feedback(models.Model):

    # Primary Key
    feedback_id = models.AutoField(primary_key=True)

    # ForeignKey to Student
    student = models.ForeignKey(
        Student,
        default=None,
        on_delete=models.CASCADE,
        db_column="student_id",
        related_name="feedbacks"  
    )

    # ForeignKey to Event
    event = models.ForeignKey(
        Event,
        default=None,
        on_delete=models.CASCADE,
        db_column="event_id",
        related_name="feedbacks"  
    )

    # Rating given by student 
    rating = models.IntegerField(default=3)


    comments = models.CharField(max_length=200, null=True, blank=True)

  
    created_at = models.DateField(auto_now_add=True, null=True)


    updated_at = models.DateField(auto_now=True, null=True)

    class Meta:
        # Custom table name
        db_table = "feedback"

