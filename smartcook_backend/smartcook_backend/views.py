from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("mainpage")  # 로그아웃 후 메인페이지 이동
    return redirect("mainpage")  # 혹시 GET으로 접근해도 그냥 메인페이지로
