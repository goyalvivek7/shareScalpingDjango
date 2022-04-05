from django.urls import path , include

from . import views
app_name = 'share'
urlpatterns = [
    path('login', views.index, name='index'),
    path('loginUser', views.loginUser),
    path('dashboard',views.dashboardView),
    path('addNewScalping',views.addNewScalping),
    path('addScalping',views.addScalping),
    path('runScalping',views.runScalping)
]