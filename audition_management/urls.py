from django.conf.urls import url
# from django.contrib import admin
from django.contrib.auth import views as auth_views
from audition_management import views


app_name = "audition_management"
urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='index'),
    # url(r'^admin/', admin.site.urls),

]
