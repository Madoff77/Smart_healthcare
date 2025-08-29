from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, Doctor
from patients.models import Patient
from .models import Appointment


class AppointmentOverlapTest(TestCase):
    def setUp(self):
        self.doc_user = User.objects.create_user(username='doc', password='x', role=User.Roles.DOCTOR)
        self.doctor = Doctor.objects.create(user=self.doc_user)
        self.pat_user = User.objects.create_user(username='pat', password='x', role=User.Roles.PATIENT)
        self.patient = Patient.objects.create(user=self.pat_user)


    def test_overlap_same_doctor(self):
        t0 = timezone.now()
        a1 = Appointment.objects.create(doctor=self.doctor, patient=self.patient, start_time=t0, end_time=t0 + timedelta(minutes=30))
        with self.assertRaises(Exception):
            Appointment.objects.create(
                doctor=self.doctor,
                patient=self.patient,
                start_time=t0 + timedelta(minutes=15),
                end_time=t0 + timedelta(minutes=45)
            )

    def test_no_overlap_different_doctor(self):
        other_doc_user = User.objects.create_user(username='doc2', password='x', role=User.Roles.DOCTOR)
        other_doctor = Doctor.objects.create(user=other_doc_user)
        t0 = timezone.now()
        Appointment.objects.create(doctor=self.doctor, patient=self.patient, start_time=t0, end_time=t0 + timedelta(minutes=30))
        # même créneau mais autre médecin => ok
        Appointment.objects.create(doctor=other_doctor, patient=self.patient, start_time=t0, end_time=t0 + timedelta(minutes=30))