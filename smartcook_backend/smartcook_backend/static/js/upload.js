// static/js/upload.js
(function () {
    // ====== 유틸 함수 ======
    function $(sel) { return document.querySelector(sel); }
    function $all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
    function show(el) { if (el) el.style.display = "block"; }
    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, m =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m])
      );
    }
  
    document.addEventListener("DOMContentLoaded", function () {
      // ====== DOM 요소 ======
      const fileInput = $("#file-upload");
      const previewImage = $("#preview-image");
      const recognizedSection = $("#ingredient-buttons");
      const recognizedList = $("#recognized-list");
      const categorySection = $("#category-section");
      const toRecipeBtn = $("#toRecipeBtn");
      const recipeSection = $("#recipe-section");
      const extraSection = $("#extra-section");
      const extraIngredientsBox = $("#extra-ingredients");
  
      const csrfInput = $("#csrf-form input[name='csrfmiddlewaretoken']");
      const CSRF = csrfInput ? csrfInput.value : "";
  
      let currentRecipeId = null;
  
      // ====== 드롭다운 처리 ======
      const dropdownToggle = $("#dropdownToggle");
      const dropdownMenu = $("#dropdownMenu");
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
              fileInput && fileInput.click(); // ✅ 파일 input 강제 클릭
            }
            dropdownMenu.style.display = "none";
          });
        });
      }
  
      // ====== 파일 선택 이벤트 ======
      if (fileInput) {
        fileInput.addEventListener("change", function (e) {
          const file = e.target.files && e.target.files[0];
          if (!file) return;
  
          // 1) 업로드한 원본 먼저 미리보기
          const reader = new FileReader();
          reader.onload = function (evt) {
            previewImage.src = evt.target.result;
            previewImage.style.display = "block";
          };
          reader.readAsDataURL(file);
  
          // 2) YOLO 호출 → 성공/실패 상관없이 다음 섹션 진행
          detectIngredients(file)
            .then(result => {
              const items = (result && result.items) ? result.items.map(it => it.name) : [];
              if (items.length > 0) {
                renderIngredientChips(items);
              } else {
                renderIngredientChips(["재료 인식 실패"]);
              }
              show(recognizedSection);
              show(categorySection);
            })
            .catch(err => {
              console.error("YOLO 인식 실패:", err);
              renderIngredientChips(["재료 인식 실패"]);
              show(recognizedSection);
              show(categorySection);
            });
        });
      }
  
      // ====== YOLO 서버 호출 ======
      function detectIngredients(file) {
        const fd = new FormData();
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
              annotated_url: data.annotated_url || null
            };
          });
      }
  
      // ====== 재료 칩 렌더링 ======
      function renderIngredientChips(ings) {
        recognizedList.innerHTML = "";
        (ings || []).forEach(name => {
          const label = document.createElement("label");
          label.className = "chip";
          label.innerHTML = `<input type="checkbox" class="chip-radio" checked /> ${escapeHtml(name)}`;
          recognizedList.appendChild(label);
        });
      }
  
      // ====== 카테고리 선택 후 서버 전송 ======
      if (toRecipeBtn) {
        toRecipeBtn.addEventListener("click", function () {
          const foodInput = $("#food-hidden-input");
          const categoriesInput = $("#categories-hidden-input");
          const spicyInput = $("#spicy-hidden-input");
  
          // 인식된 재료
          const selectedIngredients = $all("#recognized-list input:checked")
            .map(el => el.parentElement.textContent.trim().split(" ")[0])
            .filter(Boolean);
          if (foodInput) foodInput.value = selectedIngredients.join(",");
  
          // 음식 분야
          const selectedCategories = $all("#category-section .chip input:checked")
            .map(el => el.value);
          if (categoriesInput) categoriesInput.value = selectedCategories.join(",");
  
          // 매운맛
          if (spicyInput) spicyInput.value = $("#spicyRange").value;
  
          $("#recipeForm").submit();
        });
      }
  
      // ====== 레시피 결과 관련 ======
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
  
      // ====== 추가 재료 없음 ======
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
  
      // ====== 레시피 상세보기 ======
      $("#go-detail-btn")?.addEventListener("click", () => {
        if (currentRecipeId) window.location.href = `/recipes/${currentRecipeId}/`;
      });
  
      // ====== 장바구니로 이동 ======
      $("#go-cart-btn")?.addEventListener("click", () => {
        if (currentRecipeId) {
          const selected = [...document.querySelectorAll("input[name=ingredient]:checked")].map(chk => chk.value);
          const query = selected.length > 0 ? `?extra=${selected.join(",")}` : "";
          window.location.href = `/cart/${currentRecipeId}/${query}`;
        }
      });
  
      // ====== 더보기 버튼 ======
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
  