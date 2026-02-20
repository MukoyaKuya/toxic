from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import Album, Track, TourDate, ShopItem, ShopItemImage, Footer, Advertisement
import datetime
from PIL import Image
import io


def generate_test_image(size=(100, 100), color=(255, 0, 0), fmt='JPEG'):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size=size, color=color)
    image.save(file_obj, fmt)
    file_obj.seek(0)
    ext = fmt.lower()
    return SimpleUploadedFile(
        f'test_image.{ext}', file_obj.read(), content_type=f'image/{ext}'
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class AlbumModelTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title="Test Album",
            release_date=datetime.date(2023, 1, 1),
            cover_art=generate_test_image()
        )

    def test_str(self):
        self.assertEqual(str(self.album), "Test Album")

    def test_large_image_is_resized(self):
        """Cover art larger than 800px should be resized on save."""
        album = Album.objects.create(
            title="Big Cover",
            release_date=datetime.date(2024, 1, 1),
            cover_art=generate_test_image(size=(1200, 1200))
        )
        img = Image.open(album.cover_art)
        self.assertLessEqual(img.width, 800)
        self.assertLessEqual(img.height, 800)


class TrackModelTests(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title="Test Album",
            release_date=datetime.date(2023, 1, 1),
            cover_art=generate_test_image()
        )
        self.track = Track.objects.create(
            album=self.album,
            title="Test Track",
            duration=datetime.timedelta(minutes=3, seconds=30)
        )

    def test_str(self):
        self.assertEqual(str(self.track), "Test Track")


class TourDateModelTests(TestCase):
    def setUp(self):
        self.tour_date = TourDate.objects.create(
            date=timezone.now() + datetime.timedelta(days=10),
            venue="Test Venue",
            location="Test City"
        )

    def test_str(self):
        expected = f"{self.tour_date.date.strftime('%Y-%m-%d')} - Test Venue"
        self.assertEqual(str(self.tour_date), expected)

    def test_ordering(self):
        """TourDates should be ordered by date ascending."""
        later = TourDate.objects.create(
            date=timezone.now() + datetime.timedelta(days=20),
            venue="Later Venue",
            location="City B"
        )
        dates = list(TourDate.objects.all())
        self.assertEqual(dates[0], self.tour_date)
        self.assertEqual(dates[1], later)


class ShopItemModelTests(TestCase):
    def test_str(self):
        item = ShopItem.objects.create(
            title="Cool Tee",
            image=generate_test_image(),
            shop_link="https://shop.example.com/tee"
        )
        self.assertEqual(str(item), "Cool Tee")

    def test_large_image_is_resized(self):
        item = ShopItem.objects.create(
            title="Big Image Item",
            image=generate_test_image(size=(1500, 1500)),
            shop_link="https://shop.example.com/big"
        )
        img = Image.open(item.image)
        self.assertLessEqual(img.width, 1000)
        self.assertLessEqual(img.height, 1000)

    def test_default_ordering(self):
        """ShopItems should be ordered by display_order then created_at."""
        item_b = ShopItem.objects.create(
            title="Item B", image=generate_test_image(),
            shop_link="https://example.com", display_order=2
        )
        item_a = ShopItem.objects.create(
            title="Item A", image=generate_test_image(),
            shop_link="https://example.com", display_order=1
        )
        items = list(ShopItem.objects.all())
        self.assertEqual(items[0], item_a)
        self.assertEqual(items[1], item_b)


class FooterModelTests(TestCase):
    def test_singleton_load(self):
        """Footer.load() should always return pk=1 and create if missing."""
        footer = Footer.load()
        self.assertEqual(footer.pk, 1)

    def test_singleton_save_enforces_pk1(self):
        """Multiple Footer saves should still result in only one object."""
        Footer.load()
        Footer.load()
        self.assertEqual(Footer.objects.count(), 1)

    def test_str(self):
        footer = Footer.load()
        self.assertEqual(str(footer), "Footer Settings")


class AdvertisementModelTests(TestCase):
    def _make_ad(self, **kwargs):
        defaults = {
            'title': 'Test Ad',
            'image': generate_test_image(),
            'url': 'https://example.com',
            'is_active': True,
        }
        defaults.update(kwargs)
        return Advertisement(**defaults)

    def test_str_active(self):
        ad = self._make_ad()
        ad.save()
        self.assertIn('Active', str(ad))

    def test_str_inactive(self):
        ad = self._make_ad(is_active=False)
        ad.save()
        self.assertIn('Inactive', str(ad))

    def test_clean_fails_no_image_no_youtube(self):
        """clean() should raise if neither image nor youtube_link is set."""
        ad = Advertisement(title='Bad Ad')
        with self.assertRaises(ValidationError):
            ad.clean()

    def test_clean_fails_image_without_url(self):
        """clean() should raise if image provided but no url/facebook_link."""
        ad = Advertisement(title='Bad Ad', image=generate_test_image())
        with self.assertRaises(ValidationError):
            ad.clean()

    def test_clean_passes_with_youtube_only(self):
        """clean() should pass when only youtube_link is provided."""
        ad = Advertisement(title='YT Ad', youtube_link='https://youtube.com/watch?v=dQw4w9WgXcQ')
        ad.clean()  # Should not raise

    def test_clean_passes_with_image_and_url(self):
        """clean() should pass when image + url are provided."""
        ad = Advertisement(
            title='Image Ad',
            image=generate_test_image(),
            url='https://example.com'
        )
        ad.clean()  # Should not raise

    def test_save_does_not_call_clean(self):
        """Programmatic save() without required fields should not raise ValidationError."""
        # Only youtube_link — should save fine without clean() interference
        ad = Advertisement(
            title='Programmatic YT',
            youtube_link='https://youtube.com/watch?v=dQw4w9WgXcQ'
        )
        ad.save()  # Should not raise
        self.assertIsNotNone(ad.pk)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.album = Album.objects.create(
            title="Latest Album",
            release_date=datetime.date(2023, 12, 1),
            cover_art=generate_test_image()
        )

    def test_status_and_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/index.html')

    def test_context_contains_releases_and_tours(self):
        response = self.client.get(reverse('index'))
        self.assertIn('latest_releases', response.context)
        self.assertIn('upcoming_tours', response.context)
        self.assertIn(self.album, list(response.context['latest_releases']))


class MusicViewTests(TestCase):
    def test_status_and_template(self):
        response = self.client.get(reverse('music'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/music.html')


class AlbumDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.album = Album.objects.create(
            title="Detail Album",
            release_date=datetime.date(2024, 1, 1),
            cover_art=generate_test_image(),
            youtube_link='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        Track.objects.create(
            album=self.album, title="Track 1",
            youtube_link='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )

    def test_status_and_template(self):
        response = self.client.get(reverse('album_detail', args=[self.album.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/album_detail.html')

    def test_context_contains_album_and_tracks(self):
        response = self.client.get(reverse('album_detail', args=[self.album.pk]))
        self.assertEqual(response.context['album'], self.album)
        self.assertIn('tracks_with_youtube', response.context)

    def test_youtube_embed_url_in_context(self):
        response = self.client.get(reverse('album_detail', args=[self.album.pk]))
        self.assertIsNotNone(response.context['youtube_embed_url'])
        self.assertIn('/embed/', response.context['youtube_embed_url'])

    def test_active_ad_appears_in_context(self):
        ad = Advertisement.objects.create(
            title='Test Ad',
            youtube_link='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            is_active=True
        )
        response = self.client.get(reverse('album_detail', args=[self.album.pk]))
        self.assertEqual(response.context['ad'], ad)

    def test_no_active_ad_gives_none(self):
        response = self.client.get(reverse('album_detail', args=[self.album.pk]))
        self.assertIsNone(response.context['ad'])

    def test_404_for_bad_album_id(self):
        response = self.client.get(reverse('album_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class TourViewTests(TestCase):
    def test_full_render(self):
        response = self.client.get(reverse('tour'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/tour.html')

    def test_partial_render(self):
        response = self.client.get(reverse('tour') + '?partial=true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/partials/tour_list.html')


class ContactViewTests(TestCase):
    def test_status_and_template(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/contact.html')


class HealthCheckViewTests(TestCase):
    def test_returns_healthy(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'healthy'})
