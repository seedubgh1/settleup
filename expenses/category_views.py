from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View
from expenses.models import Category
from expenses.forms import CategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "expenses/category_list.html"
    context_object_name = "categories"
    ordering = ["name"]


class CategoryCreateView(LoginRequiredMixin, View):
    template_name = "expenses/category_form.html"

    def get(self, request):
        form = CategoryForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect("category_list")
        return render(request, self.template_name, {"form": form})


class CategoryEditView(LoginRequiredMixin, View):
    template_name = "expenses/category_form.html"

    def get_category(self, category_id):
        return get_object_or_404(Category, pk=category_id)

    def get(self, request, category_id):
        category = self.get_category(category_id)
        form = CategoryForm(instance=category)
        return render(request, self.template_name, {
            "form": form, "category": category,
        })

    def post(self, request, category_id):
        category = self.get_category(category_id)
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("category_list")
        return render(request, self.template_name, {
            "form": form, "category": category,
        })