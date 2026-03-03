from django.urls import path
from payments import views

urlpatterns = [
    path("", views.PaymentListView.as_view(), name="payment_list"),
    path("add/", views.PaymentCreateView.as_view(), name="payment_add"),
    path("<int:payment_id>/delete/", views.PaymentDeleteView.as_view(),
         name="payment_delete"),
]
