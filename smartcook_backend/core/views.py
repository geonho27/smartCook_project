# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
        return redirect("mainpage")  # 회원가입 성공 후 메인페이지로 이동

    return render(request, "signup.html")


# login
def login_view(request):
    if request.method == "POST":
        userid = request.POST.get("userid")  # HTML form에서는 userid
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


# mypage
@login_required
def menu2_view(request):
    user = request.user  # 로그인한 사용자

    if request.method == "POST":
        # POST 데이터 업데이트
        user.preferred_ingredients = request.POST.get("preferred", "")
        user.disliked_ingredients = request.POST.get("disliked", "")
        user.is_vegan = True if request.POST.get("is_vegan") == "on" else False
        user.allergies = request.POST.get("allergies", "")
        user.save()
        messages.success(request, "마이페이지 정보가 업데이트되었습니다.")
        return redirect("menu2")  # 저장 후 다시 마이페이지로 이동

    preferred = user.preferred_ingredients  # 예: "감자,당근"
    disliked = user.disliked_ingredients    # 예: "양파,버섯"

    return render(request, 'menu2.html', {
        'preferred': preferred,
        'disliked': disliked,
        'user': user
    })


# mainpage
def main_page(request):
    return render(request, "mainpage.html")


# upload page
def upload_page(request):
    return render(request, "upload.html")


# 단순히 menu2.html 보여주기 (혹시 따로 쓸 경우)
def mypage_view(request):
    return render(request, "menu2.html")


# logout
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("mainpage")  # 로그아웃 후 메인페이지로 이동
    return redirect("mainpage")
