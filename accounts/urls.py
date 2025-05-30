from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.profile_view, name='profile'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:     # faqat development serverda
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)