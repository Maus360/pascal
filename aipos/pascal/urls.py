from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("blogs/", views.BlogListView.as_view(), name="blogs"),
    path(
        "blog/create",
        login_required(views.BlogCreateView.as_view()),
        name="blog-create",
    ),
    path(
        "blogger/<int:pk>", views.BlogListbyAuthorView.as_view(), name="blogs-by-author"
    ),
    path("blog/<int:pk>", views.BlogDetailView.as_view(), name="blog-detail"),
    path(
        "blog/<int:pk>/delete",
        login_required(views.BlogDeleteView.as_view()),
        name="blog-delete",
    ),
    path(
        "blog/<int:pk>/update",
        login_required(views.BlogUpdateView.as_view()),
        name="blog-update",
    ),
    path("bloggers/", views.BloggerListView.as_view(), name="bloggers"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]
