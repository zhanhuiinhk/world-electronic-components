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
      subtitle: "检索型号 · 厂家 · 封装 · 分类 · 技术参数",
      searchPlaceholder: "输入型号、厂家、分类或封装…",
      searchBtn: "搜索",
      allCats: "全部分类",
      allClass: "全部类型",
      allMfr: "全部厂家",
      loaded: (n, t) => `共 ${n} 条数据 · 当前显示 ${t} 条`,
      empty: "没有找到匹配的元器件，请换个关键词试试。",
      loading: "正在加载…",
      error: "暂时无法加载数据，请稍后重试。",
      datasheet: "数据手册",
      origin: "产地",
      package: "封装",
      attrs: "技术参数",
      component: "元器件",
      part: "部件",
      module: "组件",
      navSearch: "检索",
      navDocs: "说明",
      footer: "World Electronic Components · 面向工程师的开源元器件数据",
    },
    en: {
      title: "World Electronic Components",
      subtitle: "Search part numbers, manufacturers, packages & specs",
      searchPlaceholder: "Part number, manufacturer, category, package…",
      searchBtn: "Search",
      allCats: "All categories",
      allClass: "All types",
      allMfr: "All manufacturers",
      loaded: (n, t) => `${n} parts · showing ${t}`,
      empty: "No matches. Try a different keyword.",
      loading: "Loading…",
      error: "Could not load data. Please try again later.",
      datasheet: "Datasheet",
      origin: "Origin",
      package: "Package",
      attrs: "Specifications",
      component: "Component",
      part: "Part",
      module: "Module",
      navSearch: "Search",
      navDocs: "About",
      footer: "World Electronic Components · Open data for engineers",
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
    const footer = $("#footer-text");
    if (footer) footer.textContent = t("footer");
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

  /** 参数键名友好显示（对外不展示原始内部路径） */
  function attrLabel(key) {
    const map = {
      resistance_ohm: state.lang === "zh" ? "阻值(Ω)" : "Resistance (Ω)",
      tolerance_percent: state.lang === "zh" ? "精度(%)" : "Tolerance (%)",
      power_w: state.lang === "zh" ? "功率(W)" : "Power (W)",
      composition: state.lang === "zh" ? "材质" : "Composition",
      capacitance_uf: state.lang === "zh" ? "容量(µF)" : "Capacitance (µF)",
      voltage_v: state.lang === "zh" ? "耐压(V)" : "Voltage (V)",
      core: state.lang === "zh" ? "内核" : "Core",
      flash_kb: state.lang === "zh" ? "Flash(KB)" : "Flash (KB)",
      ram_kb: state.lang === "zh" ? "RAM(KB)" : "RAM (KB)",
      clock_mhz: state.lang === "zh" ? "主频(MHz)" : "Clock (MHz)",
      gpio_count: "GPIO",
      function: state.lang === "zh" ? "功能" : "Function",
      supply_voltage_min_v: state.lang === "zh" ? "供电下限(V)" : "Vmin (V)",
      supply_voltage_max_v: state.lang === "zh" ? "供电上限(V)" : "Vmax (V)",
    };
    return map[key] || key.replace(/_/g, " ");
  }

  function renderAttrs(attrs) {
    if (!attrs || !Object.keys(attrs).length) return "";
    const bits = Object.entries(attrs)
      .map(
        ([k, v]) =>
          `<span class="attr-item"><em>${escapeHtml(attrLabel(k))}</em> ${escapeHtml(String(v))}</span>`
      )
      .join("");
    return `<div class="attrs"><strong>${t("attrs")}</strong><div class="attr-list">${bits}</div></div>`;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
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
          ? `<a href="${escapeHtml(it.datasheet_url)}" target="_blank" rel="noopener noreferrer">${t("datasheet")}</a>`
          : "—";
        return `<article class="card">
          <h3>${escapeHtml(it.part_number || "")}</h3>
          <div class="badges">
            <span class="badge green">${escapeHtml(classLabel(it.product_class))}</span>
            <span class="badge">${escapeHtml(it.category || "")}</span>
            <span class="badge purple">${escapeHtml(it.sub_category || "")}</span>
          </div>
          <div class="grid2">
            <div><strong>${escapeHtml(it.manufacturer || "")}</strong></div>
            <div>${t("package")}: <strong>${escapeHtml(it.package || "—")}</strong></div>
            <div>${t("origin")}: <strong>${escapeHtml(it.origin || "—")}</strong></div>
            <div>${ds}</div>
          </div>
          ${it.description ? `<p class="desc">${escapeHtml(it.description)}</p>` : ""}
          ${renderAttrs(it.attributes)}
        </article>`;
      })
      .join("");
  }

  function unique(arr) {
    return [...new Set(arr.filter(Boolean))].sort();
  }

  function fillFilters() {
    const cats = unique(state.items.map((i) => i.category_slug));
    const catLabels = {};
    state.items.forEach((i) => {
      if (i.category_slug) catLabels[i.category_slug] = i.category || i.category_slug;
    });
    const mfrs = unique(state.items.map((i) => i.manufacturer)).sort();
    const catSel = $("#f-cat");
    const mfrSel = $("#f-mfr");
    catSel.innerHTML =
      `<option value="">${t("allCats")}</option>` +
      cats
        .map(
          (c) =>
            `<option value="${escapeHtml(c)}">${escapeHtml(catLabels[c] || c)}</option>`
        )
        .join("");
    mfrSel.innerHTML =
      `<option value="">${t("allMfr")}</option>` +
      mfrs
        .map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`)
        .join("");
    $("#f-class").innerHTML = `
      <option value="">${t("allClass")}</option>
      <option value="component">${t("component")}</option>
      <option value="part">${t("part")}</option>
      <option value="module">${t("module")}</option>`;
  }

  function filterByManufacturerName(mfrName) {
    return state.items.filter((it) => {
      const cat = $("#f-cat").value;
      const cls = $("#f-class").value;
      const q = ($("#q").value || "").trim().toLowerCase();
      if (cat && it.category_slug !== cat) return false;
      if (cls && it.product_class !== cls) return false;
      if (mfrName && it.manufacturer !== mfrName) return false;
      if (!q) return true;
      return haystack(it).includes(q);
    });
  }

  // override filter to use manufacturer display name in select
  function filterItemsFixed() {
    const q = ($("#q").value || "").trim().toLowerCase();
    const cat = $("#f-cat").value;
    const cls = $("#f-class").value;
    const mfr = $("#f-mfr").value;
    return state.items.filter((it) => {
      if (cat && it.category_slug !== cat) return false;
      if (cls && it.product_class !== cls) return false;
      if (mfr && it.manufacturer !== mfr) return false;
      if (!q) return true;
      return haystack(it).includes(q);
    });
  }

  const _render = render;
  render = function () {
    const list = filterItemsFixed();
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
          ? `<a href="${escapeHtml(it.datasheet_url)}" target="_blank" rel="noopener noreferrer">${t("datasheet")}</a>`
          : "—";
        return `<article class="card">
          <h3>${escapeHtml(it.part_number || "")}</h3>
          <div class="badges">
            <span class="badge green">${escapeHtml(classLabel(it.product_class))}</span>
            <span class="badge">${escapeHtml(it.category || "")}</span>
            <span class="badge purple">${escapeHtml(it.sub_category || "")}</span>
          </div>
          <div class="grid2">
            <div><strong>${escapeHtml(it.manufacturer || "")}</strong></div>
            <div>${t("package")}: <strong>${escapeHtml(it.package || "—")}</strong></div>
            <div>${t("origin")}: <strong>${escapeHtml(it.origin || "—")}</strong></div>
            <div>${ds}</div>
          </div>
          ${it.description ? `<p class="desc">${escapeHtml(it.description)}</p>` : ""}
          ${renderAttrs(it.attributes)}
        </article>`;
      })
      .join("");
  };

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
