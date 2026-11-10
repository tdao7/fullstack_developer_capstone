"""Django views; demo data is explicitly fictional, API output is real when Django runs."""

import json
from datetime import date
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import FileResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from .data import DEALERS, CAR_DATA, filter_dealers, analyze_text
from .models import CarMake, CarModel, Review


def page(request, name):
    path = Path(settings.BASE_DIR) / "frontend" / "static" / name
    if not path.is_file():
        raise Http404()
    return FileResponse(path.open("rb"), content_type="text/html; charset=utf-8")


def home(request):
    return page(request, "Home.html")


def about(request):
    return page(request, "About.html")


def contact(request):
    return page(request, "Contact.html")


def register_page(request):
    return page(request, "Register.html")


def dealer_page(request, dealer_id):
    if not any(d["id"] == dealer_id for d in DEALERS):
        raise Http404()
    return page(request, "Dealer.html")


def postreview_page(request, dealer_id):
    if not any(d["id"] == dealer_id for d in DEALERS):
        raise Http404()
    return page(request, "PostReview.html")


def _wants_html(request):
    return "text/html" in request.headers.get("Accept", "")


def _payload(request):
    try:
        return json.loads(request.body or b"{}")
    except (ValueError, UnicodeError):
        return {}


@csrf_exempt  # Demo curl compatibility only; use CSRF protection in production.
@require_POST
def login_user(request):
    data = _payload(request)
    username = str(data.get("userName", data.get("username", "")))
    user = authenticate(request, username=username, password=data.get("password", ""))
    if user is None:
        return JsonResponse(
            {"userName": username, "status": "Unauthenticated"}, status=401
        )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})


@csrf_exempt  # Demo curl compatibility only.
@require_POST
def registration(request):
    data = _payload(request)
    name = str(data.get("userName", data.get("username", ""))).strip()
    passwd = str(data.get("password", ""))
    email = str(data.get("email", "")).strip()
    if not name or len(passwd) < 8 or not email:
        return JsonResponse(
            {
                "status": "Error",
                "message": "A username, email and password of >=8 characters are required",
            },
            status=400,
        )
    if User.objects.filter(username=name).exists():
        return JsonResponse(
            {"status": "Error", "message": "Username already exists"}, status=409
        )
    User.objects.create_user(
        username=name,
        password=passwd,
        email=email,
        first_name=str(data.get("firstName", "")),
        last_name=str(data.get("lastName", "")),
    )
    return JsonResponse({"userName": name, "status": "Registered"}, status=201)


@csrf_exempt  # Demo curl compatibility only.
def logout_request(request):
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Method not allowed"}, status=405)
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"})


@require_GET
def get_dealerships(request):
    if _wants_html(request):
        return home(request)
    state = request.GET.get("state")
    return JsonResponse({"status": 200, "dealers": filter_dealers(state)})


@require_GET
def get_dealers_by_state(request, state):
    if _wants_html(request):
        return home(request)
    return JsonResponse({"status": 200, "dealers": filter_dealers(state)})


@require_GET
def get_dealer_details(request, dealer_id):
    if _wants_html(request):
        return dealer_page(request, dealer_id)
    dealer = next((d for d in DEALERS if d["id"] == dealer_id), None)
    if dealer is None:
        return JsonResponse({"status": 404, "error": "Dealer not found"}, status=404)
    return JsonResponse({"status": 200, "dealer": dealer})


@require_GET
def get_dealer_reviews(request, dealer_id):
    if _wants_html(request):
        return dealer_page(request, dealer_id)
    if not any(d["id"] == dealer_id for d in DEALERS):
        return JsonResponse({"status": 404, "error": "Dealer not found"}, status=404)
    reviews = list(
        Review.objects.filter(dealership=dealer_id)
        .order_by("-id")
        .values(
            "id",
            "dealership",
            "name",
            "purchase",
            "purchase_date",
            "review",
            "car_make",
            "car_model",
            "car_year",
            "sentiment",
        )
    )
    return JsonResponse({"status": 200, "reviews": reviews})


@require_GET
def get_cars(request):
    makes = []
    for mk in CarMake.objects.prefetch_related("models").order_by("id"):
        makes.append(
            {
                "id": mk.id,
                "name": mk.name,
                "description": mk.description,
                "models": [
                    {"id": cm.id, "name": cm.name, "type": cm.type, "year": cm.year}
                    for cm in mk.models.all()
                ],
            }
        )
    cars = [
        {"CarModel": model["name"], "CarMake": make["name"]}
        for make in makes
        for model in make["models"]
    ]
    return JsonResponse({"CarModels": cars})


@require_GET
def sentiment_analysis(request, text):
    return JsonResponse({"sentiment": analyze_text(text)})


@csrf_exempt  # For this educational exercise; lock down and add CSRF in production.
@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 401, "message": "Login required"}, status=401)
    data = _payload(request)
    try:
        dealer_id = int(data.get("dealership", data.get("dealer_id")))
        year = int(data["car_year"]) if data.get("car_year") else None
    except (ValueError, TypeError):
        return JsonResponse(
            {"status": 400, "message": "Invalid dealer or year"}, status=400
        )
    if not any(d["id"] == dealer_id for d in DEALERS):
        return JsonResponse({"status": 404, "message": "Dealer not found"}, status=404)
    text = str(data.get("review", "")).strip()
    if not text:
        return JsonResponse(
            {"status": 400, "message": "Review cannot be empty"}, status=400
        )
    purchase_date = None
    if data.get("purchase_date"):
        try:
            purchase_date = date.fromisoformat(str(data["purchase_date"]))
        except ValueError:
            return JsonResponse(
                {"status": 400, "message": "Invalid purchase_date"}, status=400
            )
    obj = Review.objects.create(
        dealership=dealer_id,
        name=request.user.get_full_name() or request.user.username,
        purchase=bool(data.get("purchase", False)),
        purchase_date=purchase_date,
        review=text,
        car_make=str(data.get("car_make", "")),
        car_model=str(data.get("car_model", "")),
        car_year=year,
        sentiment=analyze_text(text),
    )
    return JsonResponse(
        {"status": 201, "message": "Review added successfully", "review_id": obj.id},
        status=201,
    )
