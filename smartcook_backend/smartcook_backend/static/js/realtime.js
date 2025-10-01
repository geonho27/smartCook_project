// 실시간 
document.addEventListener("DOMContentLoaded", function () {
    // 기본 요소들
    const loginBtn = document.querySelector(".login-button");
    const foodBtn = document.getElementById("food-btn");
    const ingredientBtn = document.getElementById("ingredient-btn");
    const foodSection = document.getElementById("food-section");
    const ingredientSection = document.getElementById("ingredient-section");
    const foodInput = document.getElementById("food-name");
    const searchIcon = foodSection ? foodSection.querySelector("img") : null;

    const recognizedSection = document.getElementById("ingredient-buttons");
    const categorySection = document.getElementById("category-section");
    const recipeSection = document.getElementById("recipe-section");
    const extraSection = document.getElementById("extra-section");
    const toCategoryBtn = document.getElementById("toCategoryBtn");
    const toRecipeBtn = document.getElementById("toRecipeBtn");

    const recipeHeaderText = document.getElementById("recipe-header-text");

    // Helper: 보이기/숨기기
    function show(section) { if (section) section.style.display = "block"; }
    function hide(section) { if (section) section.style.display = "none"; }

    // 초기 상태
    hide(recognizedSection);
    hide(categorySection);
    hide(recipeSection);
    hide(extraSection);

    // 1. 로그인
    if (loginBtn) {
      loginBtn.addEventListener("click", () => { window.location.href = "/login/"; });
    }

    // 2. 음식/재료 버튼 전환
    if (foodBtn) {
      foodBtn.addEventListener("click", () => {
        foodBtn.classList.add("active-btn");
        if (ingredientBtn) ingredientBtn.classList.remove("active-btn");
        show(foodSection);
        hide(ingredientSection);
      });
    }
    if (ingredientBtn) {
      ingredientBtn.addEventListener("click", () => {
        ingredientBtn.classList.add("active-btn");
        if (foodBtn) foodBtn.classList.remove("active-btn");
        show(ingredientSection);
        hide(foodSection);
      });
    }

    // 3. 음식명 입력 엔터 → 재료 섹션
    if (foodInput) {
      foodInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          if (foodInput.value.trim() && recognizedSection) {
            show(recognizedSection);
            recognizedSection.scrollIntoView({ behavior: "smooth" });
          }
        }
      });
    }

    // 4. 돋보기 클릭 → 재료 섹션
    if (searchIcon) {
      searchIcon.addEventListener("click", () => {
        if (foodInput.value.trim() && recognizedSection) {
          show(recognizedSection);
          recognizedSection.scrollIntoView({ behavior: "smooth" });
        }
      });
    }

    // 5. 인식된 재료 → 카테고리
    if (toCategoryBtn) {
      toCategoryBtn.addEventListener("click", () => {
        show(categorySection);
        categorySection.scrollIntoView({ behavior: "smooth" });
      });
    }

    // =============================
    // 🔥 레시피 API + 정렬 + 페이지네이션
    // =============================

    async function getRecipeRecommendations(selectedIngredients, sort="match", page=1, limit=9) {
      const query = selectedIngredients.map(q => `q=${encodeURIComponent(q)}`).join('&');
      const response = await fetch(`/api/recipes/?${query}&sort=${sort}&page=${page}&limit=${limit}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    }

    function renderRecipes(data) {
      const recipes = data.recipes;
      const recipeList = document.getElementById("recipe-list");
      recipeList.innerHTML = "";

      if (!recipes || recipes.length === 0) {
        recipeList.innerHTML = "<p>레시피를 찾을 수 없습니다.</p>";
        return;
      }

      recipes.forEach(recipe => {
        const card = document.createElement("div");
        card.classList.add("recipe-card");
        card.innerHTML = `
          <img src="${recipe.image}" alt="${recipe.title}" onerror="this.src='/static/images/recipe/muk.png'">
          <h5>${recipe.title}</h5>
          <ul>${recipe.ingredients.map(i => `<li>${i}</li>`).join('')}</ul>
          <a href="/recipes/${recipe.id}/" class="btn-category-done">요리하러 가기</a>
        `;
        recipeList.appendChild(card);
      });

      renderPagination(data.page, data.total_pages);
    }

    function renderPagination(current, total) {
      const pagination = document.getElementById("pagination");
      pagination.innerHTML = "";
      if (total <= 1) {
        pagination.style.display = "none";
        return;
      }
      pagination.style.display = "block";

      for (let i = 1; i <= total; i++) {
        const btn = document.createElement("button");
        btn.textContent = i;
        if (i === current) btn.classList.add("active");
        btn.addEventListener("click", () => {
          currentPage = i;
          loadRecipes(i, currentSort);
        });
        pagination.appendChild(btn);
      }
    }

    let currentSort = "match";
    let currentPage = 1;
    const limit = 6; // 페이지당 레시피 개수

        // 🔥 정렬 버튼 active 토글 함수 추가
    function setActiveSort(btn) {
      document.querySelectorAll(".sort-options a").forEach(el => el.classList.remove("active"));
      btn.classList.add("active");
    }

    // 정렬 버튼
    const sortMatchBtn = document.getElementById("sort-match");
    const sortIngredientsBtn = document.getElementById("sort-ingredients");

    if (sortMatchBtn) {
      sortMatchBtn.addEventListener("click", (e) => {
        e.preventDefault();
        currentSort = "match";
        currentPage = 1;   // 정렬 바뀌면 첫 페이지로
        setActiveSort(sortMatchBtn);
        loadRecipes(currentPage, currentSort);
      });
    }

    if (sortIngredientsBtn) {
      sortIngredientsBtn.addEventListener("click", (e) => {
        e.preventDefault();
        currentSort = "ingredients";
        currentPage = 1;   // 정렬 바뀌면 첫 페이지로
        setActiveSort(sortIngredientsBtn);
        loadRecipes(currentPage, currentSort);
      });
    }



    async function loadRecipes(page=1, sort=currentSort) {
      const selectedIngredients = [...document.querySelectorAll('#recognized-list input:checked')].map(el => el.value);
      if (selectedIngredients.length === 0) return;

      try {
        const data = await getRecipeRecommendations(selectedIngredients, sort, page, limit);
        renderRecipes(data);
        // 헤더 업데이트
        if (recipeHeaderText) {
          recipeHeaderText.textContent = `${selectedIngredients.join(", ")}에 대한 추천 레시피 (${data.total_count}개 중 ${data.recipes.length}개 표시)`;
        }

        show(recipeSection);
        recipeSection.scrollIntoView({ behavior: "smooth" });

      } catch (error) {
        console.error("레시피 로딩 오류:", error);
      }
    }

    // 6. 카테고리 → 레시피 이동 (여기서 실제 API 호출)
    if (toRecipeBtn) {
      toRecipeBtn.addEventListener("click", () => {
        loadRecipes(1, currentSort);
      });
    }
});