from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Blog, BlogAuthor, Comment
from .forms import CommentForm, BlogForm, BlogAuthorForm, CustomUserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse


def index(request):
    """View function for home page of site."""
    num_blogs = Blog.objects.count()
    num_authors = BlogAuthor.objects.count()

    context = {
        'num_blogs': num_blogs,
        'num_authors': num_authors,
    }
    return render(request, 'index.html', context)


class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Blog.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            ).order_by('-post_date')
        return Blog.objects.all().order_by('-post_date')


class BloggerListView(generic.ListView):
    model = User
    template_name = 'blog/blogger_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        return User.objects.all().order_by('username')


class BloggerDetailView(generic.DetailView):
    model = BlogAuthor
    template_name = 'blog/blogger_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blogger = self.get_object()
        blog_list = Blog.objects.filter(author=blogger.user)
        total_likes = sum(blog.likes.count() for blog in blog_list)
        
        context['blog_list'] = blog_list
        context['total_likes'] = total_likes
        return context


class BlogDetailView(generic.DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['comments'] = blog.comments.all()
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['is_liked'] = blog.is_liked_by(self.request.user)
        return context


@login_required
def add_comment(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.author = request.user
            comment.save()
            return redirect('blog-detail', pk=pk)
    return redirect('blog-detail', pk=pk)


@login_required
def like_blog(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        blog = get_object_or_404(Blog, pk=pk)
        
        # Toggle like
        if blog.likes.filter(id=request.user.id).exists():
            blog.likes.remove(request.user)
            liked = False
        else:
            blog.likes.add(request.user)
            liked = True
        
        # Get fresh count from database
        blog.refresh_from_db()
        current_likes = blog.likes.count()
        
        return JsonResponse({
            'liked': liked,
            'total_likes': current_likes
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. Please login.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class UserDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'blog/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['blogs'] = Blog.objects.filter(author=user).order_by('-post_date')
        context['total_blogs'] = context['blogs'].count()
        context['total_likes'] = sum(blog.total_likes() for blog in context['blogs'])
        context['total_comments'] = Comment.objects.filter(author=user).count()
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Create BlogAuthor instance if it doesn't exist
        BlogAuthor.objects.get_or_create(user=self.request.user)
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Blog post updated successfully!')
        return super().form_valid(form)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'blog/blog_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Blog post deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['blogs'] = Blog.objects.filter(author=user).order_by('-post_date')
        context['total_blogs'] = context['blogs'].count()
        context['total_likes'] = sum(blog.total_likes() for blog in context['blogs'])
        context['total_comments'] = Comment.objects.filter(author=user).count()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogAuthor
    form_class = BlogAuthorForm
    template_name = 'blog/profile_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return get_object_or_404(BlogAuthor, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
