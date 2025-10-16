# core/views.py
import json
from typing import List

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CustomUser


# ---------- 유틸: CSV <-> 리스트, 중복/공백 정리 ----------
def _csv_to_list(s: str | None) -> List[str]:
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x and x.strip()]

def _list_to_csv(items: List[str]) -> str:
    seen = set()
    out = []
    for x in items:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return ",".join(out)

def _append_unique_csv(existing_csv: str | None, item: str) -> str:
    items = _csv_to_list(existing_csv)
    item = (item or "").strip()
    if item and item not in items:
        items.append(item)
    return _list_to_csv(items)

def _remove_from_csv(existing_csv: str | None, item: str) -> str:
    items = _csv_to_list(existing_csv)
    item = (item or "").strip()
    items = [x for x in items if x != item]
    return _list_to_csv(items)

def _to_bool(v):
    # JSON true/false, "true"/"on"/"1" 등 폭넓게 처리
    return v is True or str(v).lower() in {"true", "on", "1", "yes"}


# ---------- 회원가입 ----------
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
            password=password,
        )
        return redirect("mainpage")

    return render(request, "signup.html")


# ---------- 로그인 ----------
def login_view(request):
    if request.method == "POST":
        userid = request.POST.get("userid")
        password = request.POST.get("password")

        # userid를 username 자리에 매핑하여 인증
        user = authenticate(request, username=userid, password=password)
        if user is not None:
            login(request, user)
            return redirect("mainpage")
        else:
            messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
            return render(request, "login.html")

    return render(request, "login.html")


@require_POST
@login_required
def save_preferences(request):
    # menu2_view의 POST 로직을 그대로 사용
    return menu2_view(request)

# ---------- 마이페이지 (렌더 + JSON 저장 모두 지원) ----------
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def _csv_to_list(csv_str):
    return [x.strip() for x in (csv_str or "").split(",") if x.strip()]

def _list_to_csv(items):
    return ",".join(sorted(set(_csv_to_list(",".join(items)))))

def _append_unique_csv(csv_str, val):
    items = _csv_to_list(csv_str)
    if val and val not in items:
        items.append(val)
    return ",".join(items)

def _remove_from_csv(csv_str, val):
    items = _csv_to_list(csv_str)
    return ",".join([x for x in items if x != val])

def _to_bool(val):
    if isinstance(val, bool):
        return val
    return str(val).lower() in ["1", "true", "t", "yes", "y", "on"]

# 마이페이지
@login_required
def menu2_view(request):
    user = request.user

    # JSON / Form POST 모두 처리해서 저장
    if request.method == "POST":
        try:
            # JSON 요청이면 JSON 파싱, 아니면 폼 데이터 사용
            if request.content_type and "application/json" in request.content_type.lower():
                data = json.loads(request.body or "{}")
            else:
                data = request.POST.dict()

            print("DEBUG POST DATA:", data)  # 저장 요청 확인

            updated = False

            # 비건 여부
            if "is_vegan" in data:
                user.is_vegan = _to_bool(data["is_vegan"])
                updated = True

            # 알레르기
            if "allergies" in data:
                user.allergies = (data["allergies"] or "").strip()
                updated = True

            # 선호 재료 추가 / 교체
            if "preferred" in data:
                val = (data["preferred"] or "").strip()
                if "," in val:  # "감자,당근" 같은 전체 저장
                    user.preferred_ingredients = _list_to_csv(_csv_to_list(val))
                else:
                    user.preferred_ingredients = _append_unique_csv(
                        user.preferred_ingredients, val
                    )
                updated = True

            # 선호 재료 삭제
            if "remove_preferred" in data:
                user.preferred_ingredients = _remove_from_csv(
                    user.preferred_ingredients, data["remove_preferred"]
                )
                updated = True

            # 비선호 재료 추가 / 교체
            if "disliked" in data:
                val = (data["disliked"] or "").strip()
                if "," in val:
                    user.disliked_ingredients = _list_to_csv(_csv_to_list(val))
                else:
                    user.disliked_ingredients = _append_unique_csv(
                        user.disliked_ingredients, val
                    )
                updated = True

            # 비선호 재료 삭제
            if "remove_disliked" in data:
                user.disliked_ingredients = _remove_from_csv(
                    user.disliked_ingredients, data["remove_disliked"]
                )
                updated = True

            if updated:
                user.save()
                print("DEBUG SAVED:", user.preferred_ingredients, user.disliked_ingredients)  # ✅ 저장 확인

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # ✅ GET 요청일 때 (새로고침 시 DB 값 로드)
    return render(
        request,
        "menu2.html",
        {
            "preferred": user.preferred_ingredients or "",
            "disliked": user.disliked_ingredients or "",
            "user": user,
        },
    )



# ---------- 메인/업로드/단순 렌더 ----------
def main_page(request):
    return render(request, "mainpage.html")


@login_required
def upload_page(request):
    return render(request, "upload.html")

@login_required
def live_page(request):
    return render(request, "live.html")

def mypage_view(request):
    return render(request, "menu2.html")


# ---------- 로그아웃 ----------
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("mainpage")
    return redirect("mainpage")


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

@require_POST
@login_required
def save_voice_name(request):
    try:
        data = json.loads(request.body)
        voice_name = data.get('voice_name')

        if voice_name:
            request.user.voice_name = voice_name
            request.user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No voice name provided'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import json

@login_required
def change_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_pw = data.get("current_password")
            new_pw = data.get("new_password")

            user = request.user
            if not user.check_password(current_pw):
                return JsonResponse({"success": False, "error": "현재 비밀번호가 틀렸습니다."})

            user.set_password(new_pw)
            user.save()
            update_session_auth_hash(request, user)  # 로그인 세션 유지
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "잘못된 요청"})
