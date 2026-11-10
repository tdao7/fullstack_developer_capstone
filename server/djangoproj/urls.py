from django.contrib import admin
from django.urls import include, path
from djangoapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/", include("djangoapp.urls")),
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("register", views.register_page, name="registerpage"),
    path("dealer/<int:dealer_id>", views.dealer_page, name="dealerpage"),
    path("postreview/<int:dealer_id>", views.postreview_page, name="postreviewpage"),
]
