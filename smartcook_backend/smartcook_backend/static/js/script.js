document.addEventListener("DOMContentLoaded", function () {
    // ✅ 아이디 중복확인 버튼
    const useridCheckBtn = document.querySelectorAll(".signup-check-btn")[0];
    if (useridCheckBtn) {
      useridCheckBtn.addEventListener("click", function () {
        const useridInput = document.querySelector("input[name='userid']");
        alert(`입력한 아이디 "${useridInput.value}" 는 사용 가능한지 확인 중입니다 (시뮬레이션)`);
      });
    }
  
    // ✅ 이메일 중복확인 버튼
    const emailCheckBtn = document.querySelectorAll(".signup-check-btn")[1];
    if (emailCheckBtn) {
      emailCheckBtn.addEventListener("click", function () {
        const emailInput = document.querySelector("input[name='email']");
        alert(`입력한 이메일 "${emailInput.value}" 는 사용 가능한지 확인 중입니다 (시뮬레이션)`);
      });
    }
  
    // ✅ 비밀번호 일치 확인
    const passwordInput = document.querySelector("input[name='password']");
    const passwordConfirmInput = document.querySelector("input[name='password_confirm']");
    if (passwordInput && passwordConfirmInput) {
      const warning = document.createElement("div");
      warning.style.color = "#D96C6C";
      warning.style.fontSize = "14px";
      passwordConfirmInput.parentElement.appendChild(warning);
  
      const checkMatch = () => {
        if (passwordInput.value && passwordConfirmInput.value) {
          if (passwordInput.value !== passwordConfirmInput.value) {
            warning.textContent = "비밀번호가 일치하지 않습니다.";
          } else {
            warning.textContent = "";
          }
        }
      };
  
      passwordInput.addEventListener("input", checkMatch);
      passwordConfirmInput.addEventListener("input", checkMatch);
    }
  
    // ✅ 로그인 - 아이디 저장
    const rememberIdCheckbox = document.querySelector("input[type='checkbox']");
    const loginIdInput = document.querySelector("input[name='userid']");
  
    if (rememberIdCheckbox && loginIdInput) {
      // 페이지 로드 시
      const savedId = localStorage.getItem("savedUserId");
      if (savedId) {
        loginIdInput.value = savedId;
        rememberIdCheckbox.checked = true;
      }
  
      // 체크 변경 시
      rememberIdCheckbox.addEventListener("change", function () {
        if (this.checked) {
          localStorage.setItem("savedUserId", loginIdInput.value);
        } else {
          localStorage.removeItem("savedUserId");
        }
      });
  
      // 입력값 변경 시 저장
      loginIdInput.addEventListener("input", function () {
        if (rememberIdCheckbox.checked) {
          localStorage.setItem("savedUserId", loginIdInput.value);
        }
      });
    }
  
    // ✅ 회원가입/로그인 버튼 클릭 시 비활성화 처리
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
      form.addEventListener("submit", function () {
        const submitBtn = form.querySelector("button[type='submit']");
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = "처리 중...";
        }
      });
    });
  
    // ✅ SNS 버튼 클릭 안내
    const snsButtons = document.querySelectorAll(".login-icon");
    snsButtons.forEach(btn => {
      btn.addEventListener("click", function (e) {
        alert("현재 SNS 로그인은 연동 준비 중입니다.");
      });
    });
  });
  


 // upload js
 document.addEventListener("DOMContentLoaded", function () {
    // 기본 요소들
    const loginBtn = document.querySelector(".login-button");
  
    const foodBtn = document.getElementById("food-btn");
    const ingredientBtn = document.getElementById("ingredient-btn");
  
    const foodSection = document.getElementById("food-section");
    const ingredientSection = document.getElementById("ingredient-section");
  
    const foodInput = document.getElementById("food-name");
    const searchIcon = foodSection.querySelector("img");
  
    const recognizedSection = document.getElementById("ingredient-buttons");
    const categorySection = document.getElementById("category-section");
    const recipeSection = document.getElementById("recipe-section");
    const extraSection = document.getElementById("extra-section");
  
    const toCategoryBtn = document.getElementById("toCategoryBtn");
    const toRecipeBtn = document.getElementById("toRecipeBtn");
  
    // Helper: 보이기/숨기기
    function show(section) {
      if (section) section.style.display = "block";
    }
    function hide(section) {
      if (section) section.style.display = "none";
    }
  
    // 초기에는 뒤쪽 섹션 숨김
    hide(recognizedSection);
    hide(categorySection);
    hide(recipeSection);
    hide(extraSection);
  
    // 1. 로그인 버튼 → 로그인 페이지 이동
    loginBtn?.addEventListener("click", function () {
      window.location.href = "/login/";
    });
  
    // 2. 음식/재료 버튼 전환
    foodBtn?.addEventListener("click", function () {
      foodBtn.classList.add("active-btn");
      ingredientBtn.classList.remove("active-btn");
      foodSection.style.display = "block";
      ingredientSection.style.display = "none";
    });
  
    ingredientBtn?.addEventListener("click", function () {
      ingredientBtn.classList.add("active-btn");
      foodBtn.classList.remove("active-btn");
      ingredientSection.style.display = "block";
      foodSection.style.display = "none";
    });
  
    // 3. 음식명 입력 후 엔터 → 인식된 재료로 이동
    foodInput?.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault(); // 폼 제출 막기
        const foodName = foodInput.value.trim();
        if (foodName) {
          show(recognizedSection);
          recognizedSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  
    // 4. 돋보기 클릭 → 인식된 재료로 이동
    searchIcon?.addEventListener("click", function () {
      const foodName = foodInput.value.trim();
      if (foodName) {
        show(recognizedSection);
        recognizedSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  
    // 5. 인식된 재료 → 카테고리 이동
    toCategoryBtn?.addEventListener("click", function () {
      show(categorySection);
      categorySection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  
    // 6. 카테고리 → 레시피 이동
    toRecipeBtn?.addEventListener("click", function () {
      show(recipeSection);
      recipeSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  