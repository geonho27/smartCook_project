// static/js/script.js  — 업로드/인식 + 필터링 + 추천(더보기) + (선택)GPT 재랭킹
(function () {
  // ===== 공통 유틸 =====
  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function show(el) { if (el) el.style.display = "block"; }
  function hide(el) { if (el) el.style.display = "none"; }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m];
    });
  }
  function norm(s) {
    try { return String(s).replace(/[^\p{L}]/gu, "").toLowerCase(); }
    catch (e) { return String(s).replace(/[^A-Za-z가-힣]/g, "").toLowerCase(); }
  }
  function stripQty(t) {
    return String(t)
      .replace(/\d+(\.\d+)?\s*[A-Za-z가-힣/%]+/g, "")
      .replace(/구매/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  // ===== 탭 전환 =====
  window.showSection = function (which) {
    var foodSection = $("#food-section");
    var ingredientSection = $("#ingredient-section");
    var foodBtn = $("#food-btn");
    var ingBtn = $("#ingredient-btn");

    if (which === "food") {
      show(foodSection); hide(ingredientSection);
      foodBtn && foodBtn.classList.add("active-btn");
      ingBtn && ingBtn.classList.remove("active-btn");
    } else {
      show(ingredientSection); hide(foodSection);
      ingBtn && ingBtn.classList.add("active-btn");
      foodBtn && foodBtn.classList.remove("active-btn");
    }
  };

  document.addEventListener("DOMContentLoaded", function () {
    // ===== DOM 참조 =====
    var loginBtn = $(".login-button");

    var ingredientSection = $("#ingredient-section");
    var recognizedSection = $("#ingredient-buttons");
    var categorySection   = $("#category-section");
    var recipeSection     = $("#recipe-section");

    var recognizedList = $("#recognized-list");
    var toCategoryBtn  = $("#toCategoryBtn");
    var toRecipeBtn    = $("#toRecipeBtn");

    var fileInput      = $("#file-upload");
    var previewImage   = $("#preview-image");

    var csrfInput = $("#csrf-form input[name='csrfmiddlewaretoken']");
    var CSRF = csrfInput ? csrfInput.value : "";

    // ===== 로그인 버튼 =====
    loginBtn && loginBtn.addEventListener("click", function () {
      window.location.href = "/login/";
    });

    // ===== 서버 준비 전 임시 감지 사용 여부 =====
    var FORCE_FAKE_DETECT = true;

    // ===== 파일 선택 시: 미리보기 + 인식 =====
    fileInput && fileInput.addEventListener("change", function (e) {
      var file = e.target.files && e.target.files[0];
      if (!file) return;

      // 미리보기
      try {
        var reader = new FileReader();
        reader.onload = function () {
          if (previewImage) {
            previewImage.src = reader.result;
            previewImage.style.display = "block";
          }
        };
        reader.readAsDataURL(file);
      } catch (_) {}

      // 인식된 재료 카드 열기
      show(recognizedSection);
      recognizedSection && recognizedSection.scrollIntoView &&
        recognizedSection.scrollIntoView({ behavior: "smooth", block: "start" });

      // 인식
      if (FORCE_FAKE_DETECT) {
        renderIngredientChips(fakeDetectFromFilename(file.name));
      } else {
        detectIngredients(file)
          .then(function (arr) {
            renderIngredientChips(arr && arr.length ? arr : fakeDetectFromFilename(file.name));
          })
          .catch(function () {
            renderIngredientChips(fakeDetectFromFilename(file.name));
          });
      }

      // 같은 파일을 연속 선택 가능하도록 초기화(옵션)
      // e.target.value = "";
    });

    // ===== 서버 감지 API =====
    function detectIngredients(file) {
      return new Promise(function (resolve, reject) {
        var fd = new FormData();
        fd.append("image", file);
        fetch("/api/detect/", {
          method: "POST",
          headers: CSRF ? { "X-CSRFToken": CSRF } : undefined,
          body: fd
        })
          .then(function (res) { if (!res.ok) throw new Error(res.status); return res.json(); })
          .then(function (data) { resolve((data && data.ingredients) || []); })
          .catch(reject);
      });
    }

    // ===== 파일명 폴백 감지 =====
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

    // ===== 인식 결과 칩 렌더 =====
    function renderIngredientChips(ings) {
      var box = recognizedList || $("#ingredient-buttons .chip-box");
      if (!box) return;

      var uniq = [];
      (ings || []).forEach(function (s) {
        s = String(s || "").trim();
        if (s && uniq.indexOf(s) === -1) uniq.push(s);
      });

      box.innerHTML = "";
      if (!uniq.length) {
        box.innerHTML = '<p style="padding:12px 16px;">인식된 재료가 없어요. 다른 사진으로 시도해 보세요.</p>';
        return;
      }

      uniq.forEach(function (name) {
        var label = document.createElement("label");
        label.className = "chip";
        label.innerHTML = '<input type="checkbox" class="chip-radio" checked /> ' + escapeHtml(name);
        box.appendChild(label);
      });
    }

    // ===== 인식된 재료 → 필터 카드로 이동 =====
    toCategoryBtn && toCategoryBtn.addEventListener("click", function () {
      show(categorySection);
      categorySection && categorySection.scrollIntoView &&
        categorySection.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    // ===== 레시피 JSON 로드 =====
    function loadRecipesSafe() {
      return fetch("/static/all_recipes_merged.json")
        .then(function (res) { if (!res.ok) throw new Error(res.status); return res.json(); })
        .catch(function (e) {
          console.error("레시피 JSON 로드 실패:", e);
          var listEl = $("#recipe-section .recipe-list");
          if (listEl) {
            listEl.innerHTML =
              '<p style="padding:24px;">레시피 데이터 로드에 실패했어요. <code>static/all_recipes_merged.json</code>를 확인해주세요.</p>';
          }
          return [];
        });
    }

    // ===== 필터 수집 =====
    function collectFilters() {
      var cuisines = $all("#category-section .chip input:checked")
        .map(function (el) { return (el.parentElement && el.parentElement.textContent || "").trim(); })
        .filter(Boolean);
      var spicy = Number($("#spicyRange") ? $("#spicyRange").value : 50);
      return { cuisines: cuisines, spicy: spicy };
    }

    // ===== 분야 추정 룰 =====
    var CUISINE_RULES = {
      "한식": [/김치|고추장|된장|국간장|참기름|대파|마늘|청양|떡|무침|볶음/],
      "일식": [/미림|사케|가쓰오|가츠오|우동|사시미|스시|덴푸라|가라아게/],
      "양식": [/버터|올리브|파스타|크림|오븐|스테이크|치즈|토마토\s*소스/],
      "중식": [/두반장|굴소스|춘장|마라|고추기름|볶음면|짜장|짬뽕/]
    };
    function guessCuisine(title, ingredients) {
      var text = (String(title || "") + " " + (ingredients || []).join(" ")).toLowerCase();
      for (var label in CUISINE_RULES) {
        var regs = CUISINE_RULES[label];
        for (var i = 0; i < regs.length; i++) {
          if (regs[i].test(text)) return label;
        }
      }
      return "기타";
    }

    // ===== 매운맛 추정 =====
    var SPICY_KEYS = [/고추/g, /청양/g, /마라/g, /매운/g, /칠리/g, /고춧가루/g, /고추장/g];
    function estimateSpicyLevel(title, ingredients) {
      var text = (String(title || "") + " " + (ingredients || []).join(" ")).toLowerCase();
      var hits = 0;
      SPICY_KEYS.forEach(function (re) { var m = text.match(re); if (m) hits += m.length; });
      return Math.min(100, hits * 20);
    }

    // ===== 로컬 프리필터 & 스코어 =====
    function prefilterAndScore(recipes, selected, filters) {
      var want = (selected || []).map(norm).filter(Boolean);
      var chosen = (filters.cuisines && filters.cuisines.length) ? new Set(filters.cuisines) : null;
      var spicy = Number(filters.spicy || 50);

      var out = [];
      (recipes || []).forEach(function (r) {
        var ing = (r.ingredients || []).map(function (t) { return norm(stripQty(t)); }).filter(Boolean);
        var hit = 0;
        for (var i = 0; i < want.length; i++) {
          var w = want[i];
          for (var j = 0; j < ing.length; j++) {
            var ii = ing[j];
            if (ii.indexOf(w) !== -1 || w.indexOf(ii) !== -1) { hit++; break; }
          }
        }
        if (hit === 0) return;

        var cuisineGuess = guessCuisine(r.title || "", r.ingredients || []);
        var cuisineMatch = chosen ? (chosen.has(cuisineGuess) ? 1 : 0) : 0;

        var spicyEst = estimateSpicyLevel(r.title || "", r.ingredients || []);
        var spicyDiff = Math.abs(spicyEst - spicy) / 20;
        var spicyPenalty = Math.min(2, spicyDiff);

        var score = 3 * hit + 1 * cuisineMatch - spicyPenalty;
        var id = r.id || r.title || (r.image || "");
        out.push(Object.assign({ __score: score, __cuisine: cuisineGuess, __spicy: spicyEst, id: id }, r));
      });

      out.sort(function (a, b) { return b.__score - a.__score; });
      return out;
    }

    // ===== (선택) GPT 재랭킹 =====
    async function gptRerank(candidates, selected, filters) {
      try {
        const res = await fetch("/api/rerank/", {
          method: "POST",
          headers: Object.assign({ "Content-Type": "application/json" }, CSRF ? { "X-CSRFToken": CSRF } : {}),
          body: JSON.stringify({
            selected: selected,
            cuisines: filters.cuisines,
            spicy: filters.spicy,
            candidates: candidates.map(function (r) { return { id: r.id, title: r.title, ingredients: r.ingredients }; }),
            top_k: 3
          })
        });
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        const recs = data.recommendations || [];
        if (!recs.length) return candidates;

        const map = new Map(candidates.map(function (r) { return [r.id, r]; }));
        const ranked = [];
        recs.forEach(function (it) {
          const r = map.get(it.id);
          if (r) ranked.push(Object.assign({}, r, { __gpt_score: it.score, __reason: it.reason, __missing: it.missing || [] }));
        });
        const used = new Set(ranked.map(function (r) { return r.id; }));
        candidates.forEach(function (r) { if (!used.has(r.id)) ranked.push(r); });
        return ranked;
      } catch (e) {
        console.warn("GPT rerank 사용 불가. 로컬 결과 사용:", e);
        return candidates;
      }
    }

    // ===== 3개씩 그리드 렌더 + 더보기 =====
    function renderRecipesPaginated(all) {
      var wrap = $("#recipe-section .recipe-list");
      if (!wrap) return;

      var MORE_ID = "recipe-more-wrap";
      var shown = 0;

      function renderChunk(n) {
        var slice = all.slice(shown, shown + n);
        slice.forEach(function (r) {
          var card = document.createElement("div");
          card.className = "recipe-card";
          card.innerHTML =
            '<img src="' + (r.image || "") + '" alt="' + escapeHtml(r.title || "") + '">' +
            '<h5>🍳 ' + escapeHtml(r.title || "레시피") + '</h5>' +
            '<ul>' + (r.ingredients || []).slice(0, 4).map(function (i) { return '<li>' + escapeHtml(i) + '</li>'; }).join("") + '</ul>' +
            '<button class="btn-category-done">요리하러 가기</button>';
          wrap.appendChild(card);
        });
        shown += slice.length;

        var moreWrap = $("#" + MORE_ID);
        if (!moreWrap) {
          moreWrap = document.createElement("div");
          moreWrap.id = MORE_ID;
          moreWrap.className = "more-wrap";
          recipeSection.appendChild(moreWrap);
        }
        moreWrap.innerHTML = "";
        if (shown < all.length) {
          var btn = document.createElement("button");
          btn.className = "btn-more";
          btn.textContent = "더보기";
          btn.onclick = function () { renderChunk(3); };
          moreWrap.appendChild(btn);
        }
      }

      wrap.innerHTML = "";
      var old = $("#recipe-more-wrap"); if (old) old.remove();
      renderChunk(3);
    }

    // ===== 필터 카드의 “선택 완료” 클릭 =====
    toRecipeBtn && toRecipeBtn.addEventListener("click", async function () {
      var selected = $all("#recognized-list input:checked")
        .map(function (el) { return (el.parentElement && el.parentElement.textContent || "").trim(); })
        .filter(Boolean);

      var filters = collectFilters();

      var recipes = await loadRecipesSafe();
      var pre      = prefilterAndScore(recipes, selected, filters);
      var cand15   = pre.slice(0, 15);
      var ranked   = await gptRerank(cand15, selected, filters);

      show(recipeSection);
      renderRecipesPaginated(ranked);
      recipeSection && recipeSection.scrollIntoView &&
        recipeSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
})();
