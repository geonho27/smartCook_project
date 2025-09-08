// static/js/upload.js
(function () {
    function $(sel) { return document.querySelector(sel); }
    function $all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
    function show(el) { if (el) el.style.display = "block"; }
    function hide(el) { if (el) el.style.display = "none"; }
    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, m =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m])
      );
    }
  
    document.addEventListener("DOMContentLoaded", function () {
      // ===== 업로드/인식 관련 =====
      var fileInput = $("#file-upload");
      var previewImage = $("#preview-image");
      var recognizedSection = $("#ingredient-buttons");
      var recognizedList = $("#recognized-list");
      var categorySection = $("#category-section");
      var toCategoryBtn = $("#toCategoryBtn");
      var toRecipeBtn = $("#toRecipeBtn");
      var recipeSection = $("#recipe-section");
  
      // CSRF 토큰
      var csrfInput = $("#csrf-form input[name='csrfmiddlewaretoken']");
      var CSRF = csrfInput ? csrfInput.value : "";
  
      // fake 모드 유지
      var FORCE_FAKE_DETECT = true;
  
      // 드롭다운 처리
      var dropdownToggle = $("#dropdownToggle");
      var dropdownMenu = $("#dropdownMenu");
      if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener("click", function (e) {
          e.preventDefault();
          dropdownMenu.style.display =
            dropdownMenu.style.display === "flex" ? "none" : "flex";
        });
  
        dropdownMenu.querySelectorAll("div").forEach(item => {
          item.addEventListener("click", () => {
            const choice = item.dataset.value;
            if (choice === "device" || choice === "gallery") {
              fileInput && fileInput.click(); // 파일 input 강제 트리거
            }
            dropdownMenu.style.display = "none";
          });
        });
      }
  
      // 파일 선택 이벤트
fileInput && fileInput.addEventListener("change", function (e) {
    var file = e.target.files && e.target.files[0];
    if (!file) return;
  
    // 항상 원본 미리보기 먼저 보여줌
    var reader = new FileReader();
    reader.onload = function () {
      previewImage.src = reader.result;
      previewImage.style.display = "block";
    };
    reader.readAsDataURL(file);
  
    // 서버 YOLO 호출
    detectIngredients(file).then(result => {
      if (result && result.annotated_url) {
        // YOLO 결과 이미지 있으면 교체
        previewImage.src = result.annotated_url;
        previewImage.style.display = "block";
      }
  
      // 재료가 있으면 칩 렌더링, 없으면 그냥 넘어감 (문구 없음)
      if (result && result.items && result.items.length > 0) {
        renderIngredientChips(result.items.map(it => it.name_ko));
        show(recognizedSection);
        recognizedSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }).catch(err => {
      console.error("YOLO 인식 중 오류:", err);
      // 실패해도 원본 이미지만 유지
    });
  });
  
  
  // 서버 YOLO 호출 함수 수정
  function detectIngredients(file) {
    var fd = new FormData();
    fd.append("image", file);
    return fetch("/api/detect/", {
      method: "POST",
      headers: CSRF ? { "X-CSRFToken": CSRF } : undefined,
      body: fd
    })
      .then(res => { if (!res.ok) throw new Error(res.status); return res.json(); })
      .then(data => {
        return {
          items: data.items || [],
          annotated_url: data.annotated_url || null   // ✅ 박스 친 이미지 URL
        };
      });
  }
  
  
      // 파일명 기반 가짜 인식
      function fakeDetectFromFilename(filename) {
        filename = String(filename || "").toLowerCase();
        var out = [];
        if (/kimchi|김치/.test(filename)) out.push("김치");
        if (/tofu|두부/.test(filename)) out.push("두부");
        if (/pork|돼지|목살/.test(filename)) out.push("돼지고기");
        if (/potato|감자/.test(filename)) out.push("감자");
        if (/onion|양파/.test(filename)) out.push("양파");
        if (!out.length) out = ["파", "고춧가루", "간장"];
        return out;
      }
  
      // 재료 칩 렌더링
      function renderIngredientChips(ings) {
        recognizedList.innerHTML = "";
        (ings || []).forEach(name => {
          var label = document.createElement("label");
          label.className = "chip";
          label.innerHTML = `<input type="checkbox" class="chip-radio" checked /> ${escapeHtml(name)}`;
          recognizedList.appendChild(label);
        });
      }
  
      // 인식된 재료 → 카테고리 섹션
      toCategoryBtn && toCategoryBtn.addEventListener("click", function () {
        show(categorySection);
        categorySection.scrollIntoView({ behavior: "smooth", block: "start" });
      });
  
      // 카테고리 선택 → 서버 전송
      toRecipeBtn && toRecipeBtn.addEventListener("click", function () {
        const foodInput = $("#food-hidden-input");
        const categoriesInput = $("#categories-hidden-input");
        const spicyInput = $("#spicy-hidden-input");
  
        // 인식된 재료들
        const selectedIngredients = $all("#recognized-list input:checked")
          .map(el => el.parentElement.textContent.trim().split(" ")[0])
          .filter(Boolean);
        foodInput.value = selectedIngredients.join(",");
  
        // 음식 분야
        const selectedCategories = $all("#category-section .chip input:checked")
          .map(el => el.value);
        categoriesInput.value = selectedCategories.join(",");
  
        // 매운맛
        spicyInput.value = $("#spicyRange").value;
  
        $("#recipeForm").submit();
      });
  
      // ====== 레시피 결과 관련 ======
      const extraSection = $("#extra-section");
      const extraIngredientsBox = $("#extra-ingredients");
      let currentRecipeId = null;
  
      // 요리하러 가기 → 추가재료 표시
      $all(".show-extra-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          currentRecipeId = btn.dataset.recipeId;
  
          const scriptTag = document.getElementById(`ingredients-${currentRecipeId}`);
          let ingredients = [];
          if (scriptTag) {
            try {
              ingredients = JSON.parse(scriptTag.textContent);
            } catch (e) {
              console.error("재료 JSON 파싱 실패:", e, scriptTag.textContent);
            }
          }
  
          recipeSection.style.display = "none";
          extraSection.style.display = "block";
  
          extraIngredientsBox.innerHTML = "";
          if (!ingredients || ingredients.length === 0) {
            extraIngredientsBox.innerHTML = "<p>재료가 없습니다.</p>";
          } else {
            ingredients.forEach(ing => {
              const name = ing.split(" ")[0];
              extraIngredientsBox.innerHTML += `
  <label class="chip">
    <input type="checkbox" class="chip-radio" name="ingredient" value="${name}">
    ${name}
  </label>
`;



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
      $("#go-detail-btn")?.addEventListener("click", () => {
        if (currentRecipeId) window.location.href = `/recipes/${currentRecipeId}/`;
      });
  
      // 장바구니로 이동
      $("#go-cart-btn")?.addEventListener("click", () => {
        if (currentRecipeId) {
          const selected = [...document.querySelectorAll("input[name=ingredient]:checked")].map(chk => chk.value);
          const query = selected.length > 0 ? `?extra=${selected.join(",")}` : "";
          window.location.href = `/cart/${currentRecipeId}/${query}`;
        }
      });
  
      // 더보기 (3개씩 보이기)
      const loadMoreBtn = $("#loadMoreBtn");
      if (loadMoreBtn) {
        loadMoreBtn.addEventListener("click", () => {
          const hiddenCards = document.querySelectorAll(".recipe-card[style*='display:none']");
          for (let i = 0; i < 3 && i < hiddenCards.length; i++) {
            hiddenCards[i].style.display = "block";
          }
          if (document.querySelectorAll(".recipe-card[style*='display:none']").length === 0) {
            loadMoreBtn.style.display = "none";
          }
        });
      }
    });
  })();
  