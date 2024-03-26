from django.urls import path
from .views import DataverseView, DataverseAllView, DataverseSearchView, ObjectAllView

urlpatterns = [
    path('', DataverseView.as_view(), name='dataverse'),
    path('all/', DataverseAllView.as_view(), name='dataverse_all'),
    path('objects/', ObjectAllView.as_view(), name='object_all'),
    path('search/', DataverseSearchView.as_view(), name='dataverse_search'),
]