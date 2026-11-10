"""Seed fictional course data. All users and contact details are illustrative."""

import os
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from djangoapp.models import CarMake, CarModel, Review
from djangoapp.data import CAR_DATA, SEED_REVIEWS, analyze_text


class Command(BaseCommand):
    help = "Create example car makes/models/dealer reviews and optional local demo accounts"

    def handle(self, *args, **options):
        for mk in CAR_DATA:
            make, _ = CarMake.objects.get_or_create(
                name=mk["name"], defaults={"description": mk["description"]}
            )
            for m in mk["models"]:
                CarModel.objects.get_or_create(
                    make=make,
                    name=m["name"],
                    year=m["year"],
                    defaults={"type": m["type"]},
                )
        for r in SEED_REVIEWS:
            if not Review.objects.filter(
                dealership=r["dealership"], name=r["name"], review=r["review"]
            ).exists():
                Review.objects.create(
                    **{k: v for k, v in r.items() if k != "purchase_date"},
                    purchase_date=date.fromisoformat(r["purchase_date"]),
                    sentiment=analyze_text(r["review"]),
                )
        demo_password = os.getenv("CAPSTONE_DEMO_PASSWORD")
        if demo_password:
            user, _ = User.objects.get_or_create(
                username="capstone_demo",
                defaults={
                    "first_name": "Demo",
                    "last_name": "Learner",
                    "email": "demo@example.invalid",
                },
            )
            user.set_password(demo_password)
            user.save()
        admin_password = os.getenv("CAPSTONE_ADMIN_PASSWORD")
        if admin_password:
            user, _ = User.objects.get_or_create(
                username="root", defaults={"email": "admin@example.invalid"}
            )
            user.is_staff = True
            user.is_superuser = True
            user.set_password(admin_password)
            user.save()
        self.stdout.write(
            self.style.SUCCESS(
                "Seed completed: car makes, models, reviews (and any configured demo users)."
            )
        )
