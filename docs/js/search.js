/* global fetch */
(function () {
  const $ = (sel) => document.querySelector(sel);
  const saved = localStorage.getItem("wec_lang");
  const browserZh = (navigator.language || "").toLowerCase().startsWith("zh");
  const state = {
    items: [],
    lang: saved || (browserZh ? "zh" : "en"),
  };

  const i18n = {
    zh: {
      title: "全球电子元器件开源库",
      subtitle: "在线检索型号 · 厂家 · 封装 · 分类 · 参数",
      searchPlaceholder: "搜索型号 / 厂家 / 分类 / 封装 / 标签…",
      searchBtn: "搜索",
      allCats: "全部分类",
      allClass: "全部粒度",
      allMfr: "全部厂家",
      loaded: (n, t) => `已加载 ${n} 条 · 匹配 ${t} 条`,
      empty: "没有匹配结果，试试更短的关键词。",
      loading: "正在加载目录…",
      error: "无法加载 catalog.json。请先运行 python scripts/build_catalog.py 或等待 CI 生成。",
      datasheet: "手册",
      source: "来源",
      origin: "产地",
      package: "封装",
      attrs: "参数",
      component: "元器件",
      part: "部件",
      module: "组件",
      navSearch: "检索",
      navDocs: "文档",
      navRepo: "GitHub",
    },
    en: {
      title: "World Electronic Components",
      subtitle: "Search part numbers, makers, packages, categories & attributes",
      searchPlaceholder: "Part # / manufacturer / category / package / tags…",
      searchBtn: "Search",
      allCats: "All categories",
      allClass: "All classes",
      allMfr: "All manufacturers",
      loaded: (n, t) => `Loaded ${n} · matched ${t}`,
      empty: "No matches. Try a shorter keyword.",
      loading: "Loading catalog…",
      error: "Failed to load catalog.json. Run python scripts/build_catalog.py or wait for CI.",
      datasheet: "Datasheet",
      source: "Source",
      origin: "Origin",
      package: "Package",
      attrs: "Attributes",
      component: "Component",
      part: "Part",
      module: "Module",
      navSearch: "Search",
      navDocs: "Docs",
      navRepo: "GitHub",
    },
  };

  function t(key) {
    return i18n[state.lang][key];
  }

  function applyChrome() {
    $("#brand-title").textContent = t("title");
    $("#brand-sub").textContent = t("subtitle");
    $("#q").placeholder = t("searchPlaceholder");
    $("#btn-search").textContent = t("searchBtn");
    $("#nav-search").textContent = t("navSearch");
    $("#nav-docs").textContent = t("navDocs");
    $("#nav-repo").textContent = t("navRepo");
    document.querySelectorAll("[data-lang-btn]").forEach((b) => {
      b.classList.toggle("on", b.dataset.langBtn === state.lang);
    });
    $("#nav-docs").href = state.lang === "zh" ? "./zh/" : "./en/";
  }

  function classLabel(pc) {
    if (pc === "component") return t("component");
    if (pc === "part") return t("part");
    if (pc === "module") return t("module");
    return pc || "—";
  }

  function haystack(item) {
    const parts = [
      item.part_number,
      item.manufacturer,
      item.category,
      item.sub_category,
      item.package,
      item.origin,
      item.description,
      item.product_class,
      ...(item.tags || []),
      JSON.stringify(item.attributes || {}),
    ];
    return parts.join(" ").toLowerCase();
  }

  function filterItems() {
    const q = ($("#q").value || "").trim().toLowerCase();
    const cat = $("#f-cat").value;
    const cls = $("#f-class").value;
    const mfr = $("#f-mfr").value;
    return state.items.filter((it) => {
      if (cat && it.category_slug !== cat) return false;
      if (cls && it.product_class !== cls) return false;
      if (mfr && (it.manufacturer_id || it.manufacturer) !== mfr) return false;
      if (!q) return true;
      return haystack(it).includes(q);
    });
  }

  function renderAttrs(attrs) {
    if (!attrs || !Object.keys(attrs).length) return "";
    const bits = Object.entries(attrs)
      .map(([k, v]) => `<code>${k}</code>=${escapeHtml(String(v))}`)
      .join(" · ");
    return `<div class="attrs"><strong>${t("attrs")}:</strong> ${bits}</div>`;
  }

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&")
      .replace(/</g, "<")
      .replace(/>/g, ">")
      .replace(/"/g, """);
  }

  function render() {
    const list = filterItems();
    $("#meta").textContent = t("loaded")(state.items.length, list.length);
    const root = $("#results");
    if (!list.length) {
      root.innerHTML = `<div class="empty">${t("empty")}</div>`;
      return;
    }
    root.innerHTML = list
      .slice(0, 200)
      .map((it) => {
        const ds = it.datasheet_url
          ? `<a href="${escapeHtml(it.datasheet_url)}" target="_blank" rel="noopener">${t("datasheet")}</a>`
          : "—";
        return `<article class="card">
          <h3>${escapeHtml(it.part_number || "")}</h3>
          <div class="badges">
            <span class="badge green">${escapeHtml(classLabel(it.product_class))}</span>
            <span class="badge">${escapeHtml(it.category || it.category_slug || "")}</span>
            <span class="badge purple">${escapeHtml(it.sub_category || it.sub_category_slug || "")}</span>
          </div>
          <div class="grid2">
            <div><strong>${escapeHtml(it.manufacturer || "")}</strong></div>
            <div>${t("package")}: <strong>${escapeHtml(it.package || "—")}</strong></div>
            <div>${t("origin")}: <strong>${escapeHtml(it.origin || "—")}</strong></div>
            <div>${ds}</div>
          </div>
          ${it.description ? `<p style="margin:8px 0 0;color:var(--muted);font-size:.92rem">${escapeHtml(it.description)}</p>` : ""}
          ${renderAttrs(it.attributes)}
          <div class="attrs">${t("source")}: <code>${escapeHtml(it._source || "")}</code></div>
        </article>`;
      })
      .join("");
  }

  function unique(arr) {
    return [...new Set(arr.filter(Boolean))].sort();
  }

  function fillFilters() {
    const cats = unique(state.items.map((i) => i.category_slug));
    const mfrs = unique(
      state.items.map((i) => i.manufacturer_id || i.manufacturer)
    );
    const catSel = $("#f-cat");
    const mfrSel = $("#f-mfr");
    catSel.innerHTML =
      `<option value="">${t("allCats")}</option>` +
      cats.map((c) => `<option value="${c}">${c}</option>`).join("");
    mfrSel.innerHTML =
      `<option value="">${t("allMfr")}</option>` +
      mfrs.map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
    $("#f-class").innerHTML = `
      <option value="">${t("allClass")}</option>
      <option value="component">${t("component")}</option>
      <option value="part">${t("part")}</option>
      <option value="module">${t("module")}</option>`;
  }

  async function load() {
    $("#meta").textContent = t("loading");
    try {
      const res = await fetch("./assets/catalog.json", { cache: "no-store" });
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      state.items = data.items || [];
      fillFilters();
      render();
    } catch (e) {
      $("#meta").textContent = t("error");
      $("#results").innerHTML = `<div class="empty">${t("error")}</div>`;
      console.error(e);
    }
  }

  function bind() {
    $("#btn-search").addEventListener("click", render);
    $("#q").addEventListener("keydown", (e) => {
      if (e.key === "Enter") render();
    });
    ["#f-cat", "#f-class", "#f-mfr"].forEach((sel) => {
      $(sel).addEventListener("change", render);
    });
    document.querySelectorAll("[data-lang-btn]").forEach((b) => {
      b.addEventListener("click", () => {
        state.lang = b.dataset.langBtn;
        localStorage.setItem("wec_lang", state.lang);
        applyChrome();
        fillFilters();
        render();
      });
    });
  }

  applyChrome();
  bind();
  load();
})();
