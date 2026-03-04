from django.urls import path
from expenses import category_views

urlpatterns = [
    path("", category_views.CategoryListView.as_view(), name="category_list"),
    path("add/", category_views.CategoryCreateView.as_view(), name="category_add"),
    path("<int:category_id>/edit/", category_views.CategoryEditView.as_view(), name="category_edit"),
]