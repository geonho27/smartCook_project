document.addEventListener('DOMContentLoaded', () => {
  // 로그인 버튼
  const loginBtn = document.querySelector('.login-button');
  const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
  loginBtn.textContent = isLoggedIn ? 'Logout' : 'Login';

  loginBtn.addEventListener('click', () => {
    const loggedInNow = loginBtn.textContent === 'Login';
    localStorage.setItem('loggedIn', loggedInNow ? 'true' : 'false');
    loginBtn.textContent = loggedInNow ? 'Logout' : 'Login';
  });

  // 탐색 탭 버튼
  window.showSection = function (type) {
    const foodBtn = document.getElementById('food-btn');
    const ingBtn = document.getElementById('ingredient-btn');
    const foodSection = document.getElementById('food-section');
    const ingredientSection = document.getElementById('ingredient-section');

    if (type === 'food') {
      foodBtn.classList.add('active-btn');
      ingBtn.classList.remove('active-btn');
      foodSection.style.display = 'block';
      ingredientSection.style.display = 'none';
    } else {
      ingBtn.classList.add('active-btn');
      foodBtn.classList.remove('active-btn');
      foodSection.style.display = 'none';
      ingredientSection.style.display = 'block';
    }
  };

  // 드롭다운 관련 요소
  const fileInput = document.getElementById("file-upload");
  const previewImage = document.getElementById("preview-image");
  const menu = document.getElementById("dropdownMenu");
  const toggle = document.getElementById("dropdownToggle");

  // 드롭다운 토글
  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.toggle("active");
  });

  document.addEventListener("click", () => {
    menu.classList.remove("active");
  });

  menu.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", () => {
      menu.querySelectorAll(".dropdown-item").forEach(el => el.classList.remove("selected"));
      item.classList.add("selected");
      menu.classList.remove("active");

      if (item.textContent.trim() === "기기에서") {
        fileInput.click();
      }
    });
  });

  // ✅ 동적으로 재료 UI 생성 함수
  function renderRecognizedIngredients(ingredients) {
    const chipBox = document.getElementById('recognized-list');
    chipBox.innerHTML = '';

    ingredients.forEach((ingredient, index) => {
      const label = document.createElement('label');
      label.className = 'chip';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = 'ingredient';
      input.className = 'chip-radio';

      label.appendChild(input);
      label.appendChild(document.createTextNode(' ' + ingredient));
      chipBox.appendChild(label);

      if ((index + 1) % 4 === 0) {
        const breakDiv = document.createElement('div');
        breakDiv.className = 'break';
        chipBox.appendChild(breakDiv);
      }
    });
  }

  // ✅ 파일 업로드 시 미리보기 + 재료 표시
  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.src = e.target.result;
      previewImage.style.display = "block";
      toggle.style.display = "none";
      document.getElementById("ingredient-buttons").style.display = "block";

      // 가상의 예측 결과
      const recognizedIngredients = [
        "김치", "감자", "고추가루", "당근", "돼지고기 목살", "마요네즈", "양파", "참치"
      ];

      renderRecognizedIngredients(recognizedIngredients);
    };
    reader.readAsDataURL(file);
  });
});

document.addEventListener("DOMContentLoaded", function () {
  // 🔸 첫 번째 버튼: category-section 보이게
  const toCategoryBtn = document.getElementById("toCategoryBtn");
  const categorySection = document.getElementById("category-section");

  if (toCategoryBtn) {
    toCategoryBtn.addEventListener("click", function () {
      categorySection.style.display = "block";
      categorySection.scrollIntoView({ behavior: "smooth" });
    });
  }

  // 🔸 두 번째 버튼: recipe-section 보이게
  const toRecipeBtn = document.getElementById("toRecipeBtn");
  const recipeSection = document.getElementById("recipe-section");

  if (toRecipeBtn) {
    toRecipeBtn.addEventListener("click", function () {
      recipeSection.style.display = "block";
      recipeSection.scrollIntoView({ behavior: "smooth" });
    });
  }

  // 🔸 세 번째 버튼: recipe-section 보이게
  const recipeButtons = document.querySelectorAll(".btn-category-done");
  const extraSection = document.getElementById("extra-section");

  recipeButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      extraSection.style.display = "block";
      extraSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });


  // 🔸 슬라이더 색상 동적 업데이트
  const rangeInput = document.getElementById("spicyRange");

  function updateRangeColor(val) {
    const min = rangeInput.min;
    const max = rangeInput.max;
    const percentage = ((val - min) / (max - min)) * 100;
    rangeInput.style.background = `linear-gradient(to right, #CEAB93 ${percentage}%, #dcd7d0 ${percentage}%)`;
  }

  if (rangeInput) {
    updateRangeColor(rangeInput.value); // 초기
    rangeInput.addEventListener("input", (e) => {
      updateRangeColor(e.target.value);
    });
  }
});
