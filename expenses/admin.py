from django.contrib import admin
from expenses.models import Category, Expense, ExpenseSplit

admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(ExpenseSplit)
