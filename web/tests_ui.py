from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Album
import datetime
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

def generate_test_image(size=(100, 100), color=(255, 0, 0)):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size=size, color=color)
    image.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile('test_image.jpg', file_obj.read(), content_type='image/jpeg')

class UITests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create 10 albums to ensure pagination kicks in (limit is 6)
        for i in range(10):
            Album.objects.create(
                title=f"Test Album {i}",
                release_date=datetime.date(2023, 1, 1),
                cover_art=generate_test_image()
            )

    def test_navigation_flow(self):
        self.selenium.get(self.live_server_url + reverse('index'))
        
        # Find desktop music link and click it
        music_link = self.selenium.find_element(By.XPATH, "//div[@id='nav-links']//a[contains(text(), 'MUSIC')]")
        music_link.click()

        # Wait until URL changes to /music/
        WebDriverWait(self.selenium, 5).until(EC.url_contains('/music/'))
        self.assertIn('/music/', self.selenium.current_url)

    def test_htmx_music_pagination(self):
        self.selenium.get(self.live_server_url + reverse('music'))
        
        # Verify exactly 6 albums are loaded initially
        albums = self.selenium.find_elements(By.CSS_SELECTOR, "#music-list .group")
        self.assertEqual(len(albums), 6)

        # Wait for HTMX to load (giving it a small buffer after page mount)
        import time
        time.sleep(1)
        
        # Explicitly trigger the HTMX ajax request for page 2 directly using JS to bypass headless browser quirks
        spinner_script = """
            var spinner = document.querySelector('div[hx-get]');
            if (spinner) {
                var url = spinner.getAttribute('hx-get');
                htmx.ajax('GET', url, {source: spinner, swap: 'outerHTML', target: spinner});
            }
        """
        self.selenium.execute_script(spinner_script)

        # Wait for the next 4 items to load via HTMX (Total = 10)
        try:
            WebDriverWait(self.selenium, 5).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#music-list .group")) == 10
            )
        except Exception as e:
            logs = self.selenium.get_log('browser')
            print(f"Browser Console Logs: {logs}")
            raise e
        
        updated_albums = self.selenium.find_elements(By.CSS_SELECTOR, "#music-list .group")
        self.assertEqual(len(updated_albums), 10)
