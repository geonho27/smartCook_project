# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser

# signup
def signup(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        username = request.POST.get("username")
        email = request.POST.get("email")

        if password != password_confirm:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return render(request, "signup.html")

        CustomUser.objects.create_user(
            userid=userid,
            username=username,
            email=email,
            password=password
        )
        return redirect("mainpage")  # 회원가입 성공 후 로그인 페이지로

    return render(request, "signup.html")






from django.contrib.auth import authenticate, login

# login

def login_view(request):
    if request.method == "POST":
        userid = request.POST.get("userid")  # HTML에서는 userid지만
        password = request.POST.get("password")
        
        # userid를 username 자리에 넣어줌
        user = authenticate(request, username=userid, password=password)

        if user is not None:
            login(request, user)
            return redirect("mainpage")
        else:
            messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
            return render(request, "login.html")

    return render(request, "login.html")







# mainpage

# core/views.py
from django.shortcuts import render

def main_page(request):
    return render(request, 'mainpage.html')
