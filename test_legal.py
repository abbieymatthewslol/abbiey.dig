import unittest

from app import create_app


class LegalPagesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.config.update(TESTING=True, SECRET_KEY="test")
        self.client = app.test_client()

    def test_terms_and_privacy_pages_render(self) -> None:
        r1 = self.client.get("/terms")
        self.assertEqual(r1.status_code, 200)
        self.assertIn(b"Terms of Service", r1.data)

        r2 = self.client.get("/privacy")
        self.assertEqual(r2.status_code, 200)
        self.assertIn(b"Privacy Policy", r2.data)

    def test_scan_requires_agreement(self) -> None:
        r = self.client.post(
            "/scan",
            data={
                "first_name": "",
                "middle_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "default_region": "AU",
                "usernames": "",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"You must agree", r.data)

    def test_scan_with_agreement_generates_report(self) -> None:
        r = self.client.post(
            "/scan",
            data={
                "agree": "1",
                "first_name": "",
                "middle_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "default_region": "AU",
                "usernames": "",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Digital Footprint Report", r.data)


if __name__ == "__main__":
    unittest.main()

