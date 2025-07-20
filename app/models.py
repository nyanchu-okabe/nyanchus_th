from django.db import models
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) # Hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

class Thread(models.Model):
    thread_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    password = models.CharField(max_length=128, blank=True)  # 空を許可
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # slug の自動生成
        if not self.slug:
            self.slug = slugify(self.thread_name)

        # パスワードが入力されていて、まだハッシュ化されていない場合
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.thread_name

class Comment(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True) # Temporarily allow null for migration
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.thread}: {self.content[:50]}"
