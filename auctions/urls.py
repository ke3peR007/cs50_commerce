from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("user_listing", views.user_listing, name="user_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("remove_listing/<int:listing_id>", views.remove_listing, name="remove_listing"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("add_remove_to_watchlist/<int:listing_id>", views.add_remove_to_watchlist, name="add_remove_to_watchlist"),
    path("view_watchlist", views.view_watchlist, name="view_watchlist"),
    path("add_remove_to_watchlist_index/<int:listing_id>", views.add_remove_to_watchlist_index, name="add_remove_to_watchlist_index"),
    path("view_categories", views.view_categories, name="view_categories"),
    path("category/<str:category_name>", views.category, name="category"),
]
