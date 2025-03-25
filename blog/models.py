from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class BlogAuthor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, help_text="Enter your bio details here.")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('blogger-detail', args=[str(self.id)])

    def __str__(self):
        return self.user.username


class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, help_text="Enter a brief description of your blog post.", null=True, blank=True)
    content = models.TextField(help_text="Enter your blog content here.", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)

    class Meta:
        ordering = ['-post_date']

    def get_absolute_url(self):
        return reverse('blog-detail', args=[str(self.id)])

    def total_likes(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(id=user.id).exists()

    def toggle_like(self, user):
        if self.is_liked_by(user):
            self.likes.remove(user)
            return False
        else:
            self.likes.add(user)
            return True

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(help_text="Enter your comment here.")
    post_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['post_date']

    def __str__(self):
        return f'{self.content[:50]}...' if len(self.content) > 50 else self.content
