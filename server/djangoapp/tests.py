from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from .models import Review


class CapstoneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)
        cls.user = User.objects.create_user(
            username="learner", password="ExamplePass2026!"
        )

    def test_dealers_by_kansas(self):
        data = self.client.get("/djangoapp/get_dealers/Kansas").json()
        self.assertEqual(data["status"], 200)
        self.assertGreaterEqual(len(data["dealers"]), 1)
        self.assertTrue(all(row["state"] == "Kansas" for row in data["dealers"]))

    def test_all_dealers(self):
        result = self.client.get("/djangoapp/get_dealers")
        self.assertEqual(result.status_code, 200)
        if (
            __import__("pathlib")
            .Path(__file__)
            .with_name("official_dealerships.json")
            .exists()
        ):
            self.assertEqual(len(result.json()["dealers"]), 50)

    def test_dealer_reviews(self):
        reviews = self.client.get("/djangoapp/reviews/dealer/1").json()["reviews"]
        self.assertGreater(len(reviews), 0)
        self.assertIn("purchase_date", reviews[0])

    def test_cars(self):
        result = self.client.get("/djangoapp/get_cars").json()
        self.assertIn("CarModels", result)
        self.assertGreater(len(result["CarModels"]), 0)
        self.assertIn("CarMake", result["CarModels"][0])

    def test_analyze(self):
        self.assertEqual(
            self.client.get("/djangoapp/analyze/Fantastic%20services").json()[
                "sentiment"
            ],
            "positive",
        )

    def test_login_logout(self):
        self.assertEqual(
            self.client.post(
                "/djangoapp/login",
                data='{"userName":"learner","password":"ExamplePass2026!"}',
                content_type="application/json",
            ).json()["status"],
            "Authenticated",
        )
        self.assertEqual(
            self.client.get("/djangoapp/logout").json(),
            {"userName": "", "status": "Logged out"},
        )

    def test_review_submission(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/djangoapp/add_review",
            data='{"dealership":1,"review":"Fantastic services","car_make":"Toyota","car_model":"Camry","car_year":2023}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Review.objects.filter(review="Fantastic services").exists())

    def test_pages(self):
        for path in (
            "/",
            "/about",
            "/contact",
            "/register",
            "/dealer/1",
            "/postreview/1",
        ):
            self.assertEqual(self.client.get(path).status_code, 200, path)
