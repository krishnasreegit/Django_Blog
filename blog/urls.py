from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('blogger/<int:pk>', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('blog/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('blog/<int:pk>/like/', views.like_blog, name='like-blog'),
    
    # New URLs for blog management
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('blog/create/', views.BlogCreateView.as_view(), name='blog-create'),
    path('blog/<int:pk>/update/', views.BlogUpdateView.as_view(), name='blog-update'),
    path('blog/<int:pk>/delete/', views.BlogDeleteView.as_view(), name='blog-delete'),
    
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
]
