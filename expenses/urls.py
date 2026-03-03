from django.urls import path
from expenses import views

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="expense_list"),
    path("add/", views.ExpenseCreateView.as_view(), name="expense_add"),
    path("<int:expense_id>/", views.ExpenseDetailView.as_view(),
         name="expense_detail"),
    path("<int:expense_id>/edit/", views.ExpenseEditView.as_view(),
         name="expense_edit"),
    path("<int:expense_id>/delete/", views.ExpenseDeleteView.as_view(),
         name="expense_delete"),
]
