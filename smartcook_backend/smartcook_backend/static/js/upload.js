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
    const toRecipeBtn = $("#toRecipeBtn");
    const extraSection = $("#extra-section");
    const extraIngredientsBox = $("#extra-ingredients");

    const csrfInput = $("#csrf-form input[name='csrfmiddlewaretoken']");
    const CSRF = csrfInput ? csrfInput.value : "";

    let currentRecipeId = null;

    let oauthToken;

    function onApiLoad() {
      gapi.load('auth', {'callback': onAuthApiLoad});
      gapi.load('picker', {'callback': onPickerApiLoad});
    }

    function onAuthApiLoad() {
      gapi.auth.authorize(
        {
          client_id: "983736024557-4dliicprbce97c5vvd7m9ohlfs0vdebi.apps.googleusercontent.com",   // 구글 클라우드 콘솔에서 발급
          scope: ['https://www.googleapis.com/auth/drive.file'],
          immediate: false
        },
        handleAuthResult
      );
    }

    function handleAuthResult(authResult) {
      if (authResult && !authResult.error) {
        oauthToken = authResult.access_token;
        createPicker();
      }
    }

    function onPickerApiLoad() {
      createPicker();
    }

    function createPicker() {
      if (oauthToken) {
        const picker = new google.picker.PickerBuilder()
          .addView(google.picker.ViewId.DOCS_IMAGES)
          .setOAuthToken(oauthToken)
          .setDeveloperKey("AIzaSyAp15oZqNnOOQT7XkSX58aIXZdvUcExorU")   // 구글 API 키
          .setCallback(pickerCallback)
          .build();
        picker.setVisible(true);
      } else {
        onApiLoad(); // 토큰 없으면 인증 먼저
      }
    }

    function pickerCallback(data) {
      if (data.action === google.picker.Action.PICKED) {
        const doc = data.docs[0];
        console.log("선택된 파일:", doc);

        fetch(`https://www.googleapis.com/drive/v3/files/${doc.id}?alt=media`, {
          headers: { Authorization: "Bearer " + oauthToken }
        })
        .then(res => res.blob())
        .then(blob => {
          const fd = new FormData();
          fd.append("image", blob, doc.name);
          return fetch("/api/detect/", {
            method: "POST",
            headers: CSRF ? { "X-CSRFToken": CSRF } : undefined,
            body: fd
          });
        })
        .then(res => res.json())
        .then(data => {
          console.log("YOLO 결과:", data);
          renderIngredientChips(data.items.map(it => it.name));
          show(recognizedSection);
        });
      }
    }


    // ====== 드롭다운 처리 ======
    const dropdownToggle = $("#dropdownToggle");
    const dropdownMenu = $("#dropdownMenu");
    if (dropdownToggle && dropdownMenu) {
      dropdownToggle.addEventListener("click", function (e) {
        e.preventDefault();
        console.log("드롭다운 버튼 클릭됨");
        const isVisible = dropdownMenu.style.display === "flex";
        dropdownMenu.style.display = isVisible ? "none" : "flex";
      });

      dropdownMenu.querySelectorAll("div").forEach(item => {
        item.addEventListener("click", () => {
          console.log("메뉴 클릭됨:", item.dataset.value);
          const choice = item.dataset.value;
          console.log("선택된 옵션:", choice);
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
            // 인식된 재료 섹션으로 자동 스크롤
            setTimeout(function() {
              recognizedSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
              });
            }, 300);
          })
          .catch(err => {
            console.error("YOLO 인식 실패:", err);
            renderIngredientChips(["재료 인식 실패"]);
            show(recognizedSection);
            // 인식된 재료 섹션으로 자동 스크롤
            setTimeout(function() {
              recognizedSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
              });
            }, 300);
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
        label.innerHTML = `
          <input type="checkbox" class="chip-radio" name="q" value="${escapeHtml(name)}" checked>
          ${escapeHtml(name)}
        `;
        recognizedList.appendChild(label);
      });
    }

    // ====== 선택 완료 → 레시피 검색 ======
    if (toRecipeBtn) {
      toRecipeBtn.addEventListener("click", function () {
        const selectedIngredients = $all("#recognized-list input:checked")
          .map(el => el.value)
          .filter(Boolean);

        if (selectedIngredients.length === 0) {
          alert("재료를 선택해주세요!");
          return;
        }

        const query = selectedIngredients.map(q => `q=${encodeURIComponent(q)}`).join("&");
        window.location.href = `/search_recipes_by_detected/?${query}&sort=match`;
      });
    }

    // ====== ✅ 추가재료 선택 섹션 기능 ======
    $all(".show-extra-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        currentRecipeId = btn.dataset.recipeId;

        // json_script 태그에서 재료 받아오기
        const scriptTag = document.getElementById(`ingredients-${currentRecipeId}`);
        let ingredients = [];
        if (scriptTag) {
          try {
            ingredients = JSON.parse(scriptTag.textContent);
          } catch (e) {
            console.error("재료 JSON 파싱 실패:", e, scriptTag.textContent);
          }
        }

        // ✅ recipe-section은 그대로 두고, extra-section만 표시 후 스크롤 이동
        extraSection.style.display = "block";
        extraSection.scrollIntoView({ behavior: "smooth" });

        // 칩 생성
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
              </label>
            `;
          });
        }
      });
    });

    // 추가재료 없음 → 상세보기
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

    // 상세보기로 이동
    $("#go-detail-btn")?.addEventListener("click", () => {
      if (currentRecipeId) window.location.href = `/recipes/${currentRecipeId}/`;
      else alert("먼저 요리할 레시피를 선택해주세요!");
    });

    // 장바구니로 이동
    $("#go-cart-btn")?.addEventListener("click", () => {
      if (currentRecipeId) {
        const selected = [...document.querySelectorAll("input[name=ingredient]:checked")].map(chk => chk.value);
        const query = selected.length > 0 ? `?extra=${selected.join(",")}` : "";
        window.location.href = `/cart/${currentRecipeId}/${query}`;
      } else {
        alert("먼저 요리할 레시피를 선택해주세요!");
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
