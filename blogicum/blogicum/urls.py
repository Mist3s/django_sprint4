from django.contrib import admin
from django.urls import path, include

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.page_server_error'

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
]
