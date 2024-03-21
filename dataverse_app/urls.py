from django.urls import path
from .views import DataverseView, DataverseAllView, DataverseSearchView

urlpatterns = [
    path('', DataverseView.as_view(), name='dataverse'),
    path('all/', DataverseAllView.as_view(), name='dataverse_all'),
    path('search/', DataverseSearchView.as_view(), name='dataverse_search'),
]