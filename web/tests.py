from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Album, Track, TourDate
import datetime

class ModelTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title="Test Album",
            release_date=datetime.date(2023, 1, 1),
            cover_art="covers/test.jpg"
        )
        self.track = Track.objects.create(
            album=self.album,
            title="Test Track",
            duration=datetime.timedelta(minutes=3, seconds=30)
        )
        self.tour_date = TourDate.objects.create(
            date=timezone.now() + datetime.timedelta(days=10),
            venue="Test Venue",
            location="Test City"
        )

    def test_album_str(self):
        self.assertEqual(str(self.album), "Test Album")

    def test_track_str(self):
        self.assertEqual(str(self.track), "Test Track")

    def test_tour_date_str(self):
        expected_str = f"{self.tour_date.date.strftime('%Y-%m-%d')} - Test Venue"
        self.assertEqual(str(self.tour_date), expected_str)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.album = Album.objects.create(
            title="Latest Album",
            release_date=datetime.date(2023, 12, 1),
            cover_art="covers/latest.jpg"
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/index.html')
        self.assertEqual(response.context['latest_album'], self.album)

    def test_music_view(self):
        response = self.client.get(reverse('music'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/music.html')

    def test_tour_view(self):
        response = self.client.get(reverse('tour'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/tour.html')

    def test_contact_view(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/contact.html')
