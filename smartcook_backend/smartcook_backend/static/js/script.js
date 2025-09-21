document.addEventListener("DOMContentLoaded", function () {
  // 아이디 중복확인 버튼
  const useridCheckBtn = document.querySelectorAll(".signup-check-btn")[0];
  if (useridCheckBtn) {
    useridCheckBtn.addEventListener("click", function () {
      const useridInput = document.querySelector("input[name='userid']");
      alert(`입력한 아이디 "${useridInput.value}" 는 사용 가능한지 확인 중입니다 (시뮬레이션)`);
    });
  }

  // 이메일 중복확인 버튼
  const emailCheckBtn = document.querySelectorAll(".signup-check-btn")[1];
  if (emailCheckBtn) {
    emailCheckBtn.addEventListener("click", function () {
      const emailInput = document.querySelector("input[name='email']");
      alert(`입력한 이메일 "${emailInput.value}" 는 사용 가능한지 확인 중입니다 (시뮬레이션)`);
    });
  }

  // 비밀번호 일치 확인
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

  // 로그인 - 아이디 저장
  const rememberIdCheckbox = document.querySelector("input[type='checkbox']");
  const loginIdInput = document.querySelector("input[name='userid']");

  if (rememberIdCheckbox && loginIdInput) {
    const savedId = localStorage.getItem("savedUserId");
    if (savedId) {
      loginIdInput.value = savedId;
      rememberIdCheckbox.checked = true;
    }

    rememberIdCheckbox.addEventListener("change", function () {
      if (this.checked) {
        localStorage.setItem("savedUserId", loginIdInput.value);
      } else {
        localStorage.removeItem("savedUserId");
      }
    });

    loginIdInput.addEventListener("input", function () {
      if (rememberIdCheckbox.checked) {
        localStorage.setItem("savedUserId", loginIdInput.value);
      }
    });
  }

  // 회원가입/로그인 버튼 클릭 시 비활성화 처리
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

  // SNS 버튼 클릭 안내
  const snsButtons = document.querySelectorAll(".login-icon");
  snsButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      alert("현재 SNS 로그인은 연동 준비 중입니다.");
    });
  });
});

// food_upload
document.addEventListener("DOMContentLoaded", function () {
  const recipeSection = document.getElementById("recipe-section");
  const extraSection = document.getElementById("extra-section");
  const extraIngredientsBox = document.getElementById("extra-ingredients");
  let currentRecipeId = null;

  // 요리하러 가기 → 추가 재료 표시
  document.querySelectorAll(".show-extra-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      currentRecipeId = btn.dataset.recipeId;

      // json_script로 렌더된 script 태그 찾기
      const scriptTag = document.getElementById(`ingredients-${currentRecipeId}`);
      let ingredients = [];
      if (scriptTag) {
        try {
          ingredients = JSON.parse(scriptTag.textContent);
        } catch (e) {
          console.error("재료 JSON 파싱 실패:", e, scriptTag.textContent);
        }
      }

      // ✅ 섹션을 숨기지 않고 스크롤 이동만
      extraSection.style.display = "block"; 
      extraSection.scrollIntoView({ behavior: "smooth" });

      // 재료 칩 표시
      extraIngredientsBox.innerHTML = "";
      if (!ingredients || ingredients.length === 0) {
        extraIngredientsBox.innerHTML = "<p>재료가 없습니다.</p>";
      } else {
        ingredients.forEach(ing => {
          const name = ing.split(" ")[0];
          extraIngredientsBox.innerHTML += `
<label class="chip">
  <input type="checkbox" class="chip-radio" name="ingredient" value="${name}">
  <span>${name}</span>
</label>`;
        });
      }
    });
  });

  // 추가 재료 없음 →
  const skipBtn = document.getElementById("skip-extra-btn");
  if (skipBtn) {
    skipBtn.addEventListener("click", () => {
      if (currentRecipeId) {
        window.location.href = `/recipes/${currentRecipeId}/`;
      } else {
        alert("먼저 요리할 레시피를 선택해주세요!");
      }
    });
  }

  // 레시피 상세보기
  const detailBtn = document.getElementById("go-detail-btn");
  if (detailBtn) {
    detailBtn.addEventListener("click", () => {
      if (currentRecipeId) {
        window.location.href = `/recipes/${currentRecipeId}/`;
      }
    });
  }

  // 장바구니로 이동
  const cartBtn = document.getElementById("go-cart-btn");
  if (cartBtn) {
    cartBtn.addEventListener("click", () => {
      if (currentRecipeId) {
        const selected = [...document.querySelectorAll("input[name=ingredient]:checked")]
          .map(chk => chk.value);
        const query = selected.length > 0 ? `?extra=${selected.join(",")}` : "";
        window.location.href = `/cart/${currentRecipeId}/${query}`;
      }
    });
  }

  // ✅ 더보기 버튼
  const loadMoreBtn = document.getElementById("loadMoreBtn");
  if (loadMoreBtn) {
    const cards = document.querySelectorAll(".recipe-card");
    let visibleCount = 3;

    cards.forEach((card, idx) => {
      if (idx >= visibleCount) {
        card.style.display = "none";
      }
    });

    loadMoreBtn.addEventListener("click", () => {
      let newVisible = visibleCount + 3;
      for (let i = visibleCount; i < newVisible && i < cards.length; i++) {
        cards[i].style.display = "block";
      }
      visibleCount = newVisible;

      if (visibleCount >= cards.length) {
        loadMoreBtn.style.display = "none";
      }
    });
  }
});

// mainpage
document.addEventListener("DOMContentLoaded", function () {
  const startCookingButton = document.querySelector(".home-start");
  if (startCookingButton) {
    const uploadUrl = startCookingButton.dataset.uploadUrl;
    const loginUrl = startCookingButton.dataset.loginUrl;
    const isAuthenticated = JSON.parse(document.body.dataset.isAuthenticated);

    startCookingButton.addEventListener("click", function (event) {
      if (!isAuthenticated) {
        event.preventDefault();
        alert("로그인 후 이용해 주세요.");
        window.location.href = loginUrl;
      } else {
        window.location.href = uploadUrl;
      }
    });
  }
});

// cart
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".plus-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const countEl = btn.parentElement.querySelector(".cart-count");
      let count = parseInt(countEl.textContent, 10);
      countEl.textContent = count + 1;
    });
  });

  document.querySelectorAll(".minus-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const countEl = btn.parentElement.querySelector(".cart-count");
      let count = parseInt(countEl.textContent, 10);
      if (count > 1) {
        countEl.textContent = count - 1;
      }
    });
  });

  document.querySelectorAll(".cart-trash").forEach(trash => {
    trash.addEventListener("click", () => {
      const wrapper = trash.closest(".cart-item-wrapper");
      wrapper.remove();
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const coupangBtn = document.getElementById("go-coupang");
  if (coupangBtn) {
    coupangBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.open("https://www.coupang.com/", "_blank");
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const from = params.get("from");
  const recipeId = params.get("recipe");

  if (from === "extra" && recipeId) {
    const btn = document.querySelector(`.show-extra-btn[data-recipe-id="${recipeId}"]`);
    if (btn) {
      btn.click();
    }
  }
});
