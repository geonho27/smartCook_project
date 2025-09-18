// static/js/upload.js
(function () {
  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function show(el) { if (el) el.style.display = "block"; }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, m =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m])
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    const fileInput = $("#file-upload");
    const previewImage = $("#preview-image");
    const recognizedSection = $("#ingredient-buttons");
    const recognizedList = $("#recognized-list");
    const categorySection = $("#category-section");
    const toRecipeBtn = $("#toRecipeBtn");
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
            fileInput && fileInput.click();
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

        // 업로드한 원본 미리보기
        const reader = new FileReader();
        reader.onload = function (evt) {
          previewImage.src = evt.target.result;
          previewImage.style.display = "block";

          const dropdown = document.querySelector(".dropdown");
          if (dropdown) {
            dropdown.style.display = "none";
            dropdown.style.visibility = "hidden";
          }
        };
        reader.readAsDataURL(file);

        // YOLO 호출
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

    // ====== 카테고리 선택 후 서버 전송 (render 방식) ======
    if (toRecipeBtn) {
      toRecipeBtn.addEventListener("click", function () {
        const selectedIngredients = $all("#recognized-list input:checked")
          .map(el => el.parentElement.textContent.trim())
          .filter(Boolean);

        if (selectedIngredients.length === 0) {
          alert("재료를 선택해주세요!");
          return;
        }

        const query = encodeURIComponent(selectedIngredients.join(","));
        window.location.href = `/search_recipes_by_detected/?q=${query}&sort=match`;
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

    $("#go-detail-btn")?.addEventListener("click", () => {
      if (currentRecipeId) window.location.href = `/recipes/${currentRecipeId}/`;
    });

    $("#go-cart-btn")?.addEventListener("click", () => {
      if (currentRecipeId) {
        const selected = [...document.querySelectorAll("input[name=ingredient]:checked")].map(chk => chk.value);
        const query = selected.length > 0 ? `?extra=${selected.join(",")}` : "";
        window.location.href = `/cart/${currentRecipeId}/${query}`;
      }
    });

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
