from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# signup
class CustomUserManager(BaseUserManager):
    def create_user(self, userid, username, email, password=None, **extra_fields):
        if not userid:
            raise ValueError("아이디(userid)는 필수입니다.")
        if not email:
            raise ValueError("이메일은 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(userid=userid, username=username, email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(userid, username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    userid = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "userid"
    REQUIRED_FIELDS = ["username", "email"]

    def __str__(self):
        return self.userid
