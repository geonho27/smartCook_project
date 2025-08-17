// script.js

// ==================== cart ====================
if (document.getElementById('cartItemsContainer')) {
  const cartData = [
    { name: "통깨", count: 3 },
    { name: "소금", count: 1 },
    { name: "깻잎", count: 2 },
    { name: "설탕", count: 2 },
    { name: "후추", count: 1 }
  ];

  function createCartItem(item) {
    const wrapper = document.createElement('div');
    wrapper.className = 'cart-item-wrapper';

    wrapper.innerHTML = `
      <div class="cart-item">
        <span class="cart-item-name">${item.name}</span>
        <div class="cart-btn-group">
          <button class="cart-btn plus">+</button>
          <button class="cart-btn minus">-</button>
          <span class="cart-count">${item.count}</span>
        </div>
      </div>
      <img class="cart-trash" src="../images/cart/trash.png" alt="삭제">
    `;

    const plusBtn = wrapper.querySelector('.plus');
    const minusBtn = wrapper.querySelector('.minus');
    const countSpan = wrapper.querySelector('.cart-count');

    plusBtn.addEventListener('click', () => {
      let count = parseInt(countSpan.textContent);
      countSpan.textContent = count + 1;
    });

    minusBtn.addEventListener('click', () => {
      let count = parseInt(countSpan.textContent);
      if (count > 1) countSpan.textContent = count - 1;
    });

    const trashBtn = wrapper.querySelector('.cart-trash');
    trashBtn.addEventListener('click', () => {
      wrapper.remove();
    });

    return wrapper;
  }

  const container = document.getElementById('cartItemsContainer');
  cartData.forEach(item => {
    const element = createCartItem(item);
    container.appendChild(element);
  });

  const goBtn = document.querySelector('.cart-go-button');
  if (goBtn) {
    goBtn.addEventListener('click', () => {
      const cart = [];
      document.querySelectorAll('.cart-item-wrapper').forEach(wrapper => {
        const name = wrapper.querySelector('.cart-item-name').textContent;
        const count = parseInt(wrapper.querySelector('.cart-count').textContent);
        cart.push({ name, count });
      });
      // TODO: 장바구니 서버 연동 가능. 지금은 외부로 이동(임시).
      window.location.href = "https://www.coupang.com/";
    });
  }
}


// ==================== login ====================
if (document.getElementById('username') && document.getElementById('password')) {
  function handleLogin() {
    const username = document.getElementById('username')?.value.trim();
    const password = document.getElementById('password')?.value.trim();

    if (!username || !password) {
      alert("아이디와 비밀번호를 모두 입력해주세요!");
      return;
    }

    console.log("입력된 아이디:", username);
    console.log("입력된 비밀번호:", password);

    alert(`${username}님 환영합니다! 🎉`);
  }
}


// ==================== signup ====================
if (document.querySelectorAll('.signup-check-btn').length > 0) {
  document.querySelectorAll('.signup-check-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      const field = input.name === 'userid' ? '아이디' : '이메일';
      const value = input.value.trim();

      if (!value) {
        alert(`${field}를 입력해주세요.`);
      } else {
        alert(`${field} \"${value}\"는 사용 가능합니다! (임시)`);
      }
    });
  });
}

if (document.querySelector('form')) {
  document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();

    const userid = document.querySelector('input[name="userid"]').value.trim();
    const password = document.querySelector('input[name="password"]').value.trim();
    const password_confirm = document.querySelector('input[name="password_confirm"]').value.trim();
    const username = document.querySelector('input[name="username"]').value.trim();
    const email = document.querySelector('input[name="email"]').value.trim();

    if (!userid || !password || !password_confirm || !username || !email) {
      alert('모든 필수 항목을 입력해주세요!');
      return;
    }

    if (password !== password_confirm) {
      alert('비밀번호가 일치하지 않습니다!');
      return;
    }

    alert(`${username}님, 회원가입을 환영합니다! 🎉`);
  });
}


// ==================== menu1 ====================
document.addEventListener('DOMContentLoaded', () => {
  const changeBtn = document.querySelector('.menu-password-change-box');
  if (changeBtn) {
    changeBtn.addEventListener('click', () => {
      const confirmed = confirm("비밀번호를 변경하시겠습니까?");
      if (confirmed) {
        alert("비밀번호 변경 페이지로 이동합니다! (임시)");
        window.location.href = 'change-password.html';
      }
    });
  }
});


// ==================== menu2 ====================

// 재료 태그 추가 유틸
function addIngredient(inputEl, containerEl) {
  const value = inputEl.value.trim();
  if (!value) return;

  const exists = Array.from(containerEl.children).some(child => child.textContent === value);
  if (exists) {
    alert(`이미 "${value}"은(는) 입력되어 있어요!`);
    inputEl.value = '';
    return;
  }

  const tag = document.createElement('div');
  tag.className = 'menu2-tag-button';
  tag.textContent = value;
  containerEl.appendChild(tag);

  inputEl.value = '';
}

// 엔터 입력 이벤트 등록
document.addEventListener('DOMContentLoaded', () => {
  const preferInput = document.getElementById('prefer-input');
  const nonpreferInput = document.getElementById('nonprefer-input');
  const preferTags = document.getElementById('prefer-tags');
  const nonpreferTags = document.getElementById('nonprefer-tags');

  if (preferInput && preferTags) {
    preferInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addIngredient(preferInput, preferTags);
      }
    });
  }

  if (nonpreferInput && nonpreferTags) {
    nonpreferInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addIngredient(nonpreferInput, nonpreferTags);
      }
    });
  }
});


// ==================== recipe (단일 레시피 페이지 유틸; 필요 시 사용) ====================

const recipeData = {
  "mukchi": {
    title: "묵은지 참치말이 레시피 (2인분)",
    ingredients: [
      "잡곡밥 1.5공기 (300g)",
      "참치 통조림 (소) 2개",
      "묵은지 6~8장",
      "마요네즈 2큰술",
      "후추 약간",
      "깻잎 10장 내외",
      "들기름 약간",
      "통깨 약간",
      "소금 약간"
    ],
    steps: [
      "묵은지는 물에 깨끗하게 씻은 후 체에 받쳐 물기를 제거해 주세요.",
      "참치 통조림은 기름을 쫙 따라낸 후, 마요네즈와 후추를 약간 넣고 골고루 섞어줍니다.",
      "따뜻한 잡곡밥에 소금과 들기름을 약간 넣고 골고루 비벼줍니다.",
      "김밥 위에 묵은지를 겹쳐서 넓게 펼칩니다.",
      "묵은지 위에 밥을 고르게 펴고, 깻잎을 올린 후 마요네즈에 버무린 참치를 올려 돌돌 말아주세요.",
      "묵은지 말이 겉면에 들기름을 살짝 바른 후 먹기 좋은 크기로 썰어줍니다.",
      "접시에 예쁘게 담고 통깨를 솔솔 뿌려주면 완성!"
    ],
    youtubeQuery: "묵은지 참치말이"
  },
  // 필요 시 확장
};

// 유튜브 썸네일 가져오기(키 필요)
async function fetchYoutubeVideos(query) {
  const apiKey = "API_KEY"; // TODO: 유튜브 API 키로 교체
  const maxResults = 4;

  const apiUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=${maxResults}&key=${apiKey}`;

  try {
    const res = await fetch(apiUrl);
    const data = await res.json();
    if (!data.items) return [];
    return data.items.map(item => ({
      videoId: item.id.videoId,
      title: item.snippet.title,
      thumbnail: item.snippet.thumbnails.medium.url
    }));
  } catch (err) {
    console.error("YouTube API Error:", err);
    return [];
  }
}

function renderRecipe(recipe) {
  // 제목
  const sub = document.querySelector('.recipe-subheading');
  if (sub) sub.innerHTML = `<strong>🥢 ${recipe.title}</strong>`;

  // 재료 목록: 위치 의존도가 높아서 안전하게 탐색
  const ingredientsUL = sub ? sub.nextElementSibling?.nextElementSibling : null;
  if (ingredientsUL) {
    const ingredientsHTML = recipe.ingredients.map(item => `<li>${item}</li>`).join('');
    ingredientsUL.innerHTML = ingredientsHTML;
  }

  // 만드는 법
  const ol = document.querySelector('ol');
  if (ol) {
    const stepsHTML = recipe.steps.map(step => `<li>${step}</li>`).join('');
    ol.innerHTML = stepsHTML;
  }
}

function renderYoutubeThumbnails(videos) {
  const container = document.querySelector('.recipe-right-box');
  if (!container) return;
  let html = `<h2>유튜브 영상 보러가기</h2>`;
  videos.forEach(video => {
    html += `
      <a href="https://www.youtube.com/watch?v=${video.videoId}" target="_blank">
        <img class="recipe-video-slot" src="${video.thumbnail}" alt="${video.title}" title="${video.title}">
      </a>
    `;
  });
  container.innerHTML = html;
}

// ✅ (버그 수정) loadRecipe의 중괄호가 어긋나 있었음. 정리 완료.
async function loadRecipe() {
  const foodId = localStorage.getItem("selectedFood");
  const recipe = recipeData[foodId];
  if (!recipe) return;

  renderRecipe(recipe);
  const youtubeResults = await fetchYoutubeVideos(recipe.youtubeQuery);
  renderYoutubeThumbnails(youtubeResults);
}
document.addEventListener("DOMContentLoaded", loadRecipe);


// ==================== upload.html 전용: 탭/업로드/추천 흐름 + 서버 API 연동 ====================

document.addEventListener('DOMContentLoaded', () => {
  // 로그인 버튼 토글
  const loginBtn = document.querySelector('.login-button');
  if (loginBtn) {
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    loginBtn.textContent = isLoggedIn ? 'Logout' : 'Login';
    loginBtn.addEventListener('click', () => {
      const loggedInNow = loginBtn.textContent === 'Login';
      localStorage.setItem('loggedIn', loggedInNow ? 'true' : 'false');
      loginBtn.textContent = loggedInNow ? 'Logout' : 'Login';
    });
  }

  // 탭 전환
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
      foodSection.scrollIntoView({ behavior: 'smooth' });
    } else {
      ingBtn.classList.add('active-btn');
      foodBtn.classList.remove('active-btn');
      foodSection.style.display = 'none';
      ingredientSection.style.display = 'block';
      ingredientSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // 드롭다운/업로드 UI
  const fileInput = document.getElementById("file-upload");
  const previewImage = document.getElementById("preview-image");
  const menu = document.getElementById("dropdownMenu");
  const toggle = document.getElementById("dropdownToggle");

  if (toggle && menu) {
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
        if (item.textContent.trim() === "기기에서" && fileInput) {
          fileInput.click();
        }
      });
    });
  }

  // ✅ 동적으로 재료 UI 생성
  function renderRecognizedIngredients(ingredients) {
    const chipBox = document.getElementById('recognized-list');
    if (!chipBox) return;
    chipBox.innerHTML = '';

    ingredients.forEach((ingredient, index) => {
      const label = document.createElement('label');
      label.className = 'chip';

      const input = document.createElement('input');
      input.type = 'checkbox';
      input.name = 'ingredient';
      input.className = 'chip-radio';
      input.value = ingredient;

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

  // ✅ 파일 업로드 시 미리보기 + (임시) 인식 결과 렌더
  if (fileInput) {
    fileInput.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        if (previewImage) {
          previewImage.src = e.target.result;
          previewImage.style.display = "block";
        }
        if (toggle) toggle.style.display = "none";
        const ingButtons = document.getElementById("ingredient-buttons");
        if (ingButtons) {
          ingButtons.style.display = "block";
          ingButtons.scrollIntoView({ behavior: "smooth" });
        }

        // TODO: 서버에 업로드하여 실제 인식 결과 받기 (/api/upload/ingredient)
        // 지금은 가상 예측 결과
        const recognizedIngredients = ["김치", "감자", "고추가루", "당근", "돼지고기 목살", "마요네즈", "양파", "참치"];
        renderRecognizedIngredients(recognizedIngredients);
      };
      reader.readAsDataURL(file);
    });
  }

  // 🔸 다음 단계 버튼들
  const toCategoryBtn = document.getElementById("toCategoryBtn");
  const toRecipeBtn = document.getElementById("toRecipeBtn");
  const categorySection = document.getElementById("category-section");
  const recipeSection = document.getElementById("recipe-section");
  const extraSection = document.getElementById("extra-section");

  if (toCategoryBtn && categorySection) {
    toCategoryBtn.addEventListener("click", function () {
      categorySection.style.display = "block";
      categorySection.scrollIntoView({ behavior: "smooth" });
    });
  }

  // ✅ (API 연동) 음식명 검색: 돋보기/엔터 → /api/search/food 호출
  const foodNameInput = document.getElementById('food-name');
  const foodSearchBtn = document.querySelector('#food-section .input-wrapper img'); // 돋보기 이미지

  async function callFoodSearch() {
    const q = (foodNameInput?.value || '').trim();
    if (!q) { alert('음식명을 입력해 주세요!'); foodNameInput?.focus(); return; }

    try {
      const res = await fetch(`/api/search/food?q=${encodeURIComponent(q)}`);
      if (!res.ok) throw new Error('검색 실패');
      const data = await res.json(); // {query, session_id, results}

      // 다음 단계에서 쓸 세션 저장
      if (data.session_id) sessionStorage.setItem('smartcook:sessionId', String(data.session_id));

      // 원페이지 플로우 유지: 선호도로 이동
      if (categorySection) {
        categorySection.style.display = "block";
        categorySection.scrollIntoView({ behavior: "smooth" });
      }
    } catch (e) {
      console.error(e);
      alert('검색 중 오류가 발생했어요 😥');
    }
  }

  if (foodSearchBtn) foodSearchBtn.addEventListener('click', callFoodSearch);
  if (foodNameInput) {
    foodNameInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); callFoodSearch(); }
    });
  }

  // ✅ (API 연동) 추천 호출: 선호도 완료 → /api/recommend 호출
  if (toRecipeBtn && recipeSection) {
    toRecipeBtn.addEventListener("click", async function () {
      try {
        const sessionId = Number(sessionStorage.getItem('smartcook:sessionId') || 0);

        // 1) 인식된 재료 체크박스에서 선택된 것
        const selectedFromRecognized = Array
          .from(document.querySelectorAll('input[name="ingredient"]:checked'))
          .map(i => i.value.trim());

        // 2) 추가 재료(있다면)도 함께
        const selectedExtra = Array
          .from(document.querySelectorAll('input[name="extra"]:checked'))
          .map(i => i.parentElement.textContent.trim());

        const ingredients = [...selectedFromRecognized, ...selectedExtra];

        // 빈 배열이면 서버는 처리하긴 하지만 UX상 알려주기
        if (ingredients.length === 0) {
          if (!confirm('선택된 재료가 없어요. 그래도 추천을 받아볼까요?')) {
            return;
          }
        }

        const res = await fetch('/api/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId, ingredients })
        });
        if (!res.ok) throw new Error('추천 실패');

        const data = await res.json(); // {results:[{id,title,score}], mode}
        renderRecipes(data.results);

        recipeSection.style.display = "block";
        recipeSection.scrollIntoView({ behavior: "smooth" });
      } catch (e) {
        console.error(e);
        alert('추천 중 오류가 발생했어요 😥');
      }
    });
  }

  // 🔸 “요리하러 가기” → 추가 재료 섹션
  const recipeButtons = document.querySelectorAll(".btn-category-done");
  if (recipeButtons && extraSection) {
    recipeButtons.forEach((btn) => {
      btn.addEventListener("click", function () {
        extraSection.style.display = "block";
        extraSection.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

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

  // ✅ 추천 결과를 기존 .recipe-list 컨테이너에 네 카드 스타일로 렌더
  function renderRecipes(list) {
    const listEl = document.querySelector(".recipe-list");
    if (!listEl) return;

    listEl.innerHTML = ""; // 기존 카드 초기화(원하면 append 방식으로 변경 가능)

    list.forEach(item => {
      const card = document.createElement("div");
      card.className = "recipe-card";

      card.innerHTML = `
        <img src="/static/images/kimchi.png" alt="${item.title}">
        <h5>🥢${item.title}</h5>
        <ul>
          <li>추천 점수: ${item.score ?? '-'}</li>
          <li>소요 시간: 20~30분 (예시)</li>
          <li>재료: 모델 연결 후 표시</li>
        </ul>
        <button class="btn-category-done">요리하러 가기</button>
      `;

      listEl.appendChild(card);
    });

    // 새로 그린 카드의 버튼에도 동일 동작 부여
    listEl.querySelectorAll(".btn-category-done").forEach(btn => {
      btn.addEventListener("click", () => {
        if (extraSection) {
          extraSection.style.display = "block";
          extraSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });
  }
});

