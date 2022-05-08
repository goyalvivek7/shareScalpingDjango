from django.urls import path , include

from . import views
app_name = 'share'
urlpatterns = [
    path('login', views.index, name='index'),
    path('loginUser', views.loginUser),
    path('dashboard',views.dashboardView),
    path('addNewScalping',views.addNewScalping),
    path('addScalping',views.addScalping),
    path('runScalping',views.runScalping),
    path('stopscalping',views.cancelOrder),
    path('addToFav',views.addToFav),
    path('deleteScalping',views.deleteScalping),
    path('editScalping',views.editScalping),
    path('openEditScalping',views.openEditScalping),
    path('updateScalping',views.updateScalpingOrder),
    path('openMyFavourite',views.openMyFavourite),
    path('deleteFav',views.deleteFavourite),
    path('logoutUser',views.logoutUser),
]