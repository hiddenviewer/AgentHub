document.addEventListener("DOMContentLoaded", () => {
  // state
  let newsData = [];
  let resourcesData = [];
  let currentFilter = "all";
  let searchQuery = "";

  // DOM Elements
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const newsGrid = document.getElementById("news-grid");
  const resourcesContainer = document.getElementById("resources-container");
  const searchInput = document.getElementById("news-search");
  const filterBtns = document.querySelectorAll(".filter-btn");

  // Init
  init();

  function init() {
    setupTabs();
    setupFilters();
    fetchData();
  }

  // Tab switching logic
  function setupTabs() {
    tabBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const target = btn.getAttribute("data-target");

        // Update active tab button
        tabBtns.forEach(b => {
          b.classList.remove("active");
          b.setAttribute("aria-selected", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");

        // Show active tab pane
        tabPanes.forEach(pane => {
          if (pane.id === target) {
            pane.classList.add("active");
          } else {
            pane.classList.remove("active");
          }
        });
      });
    });
  }

  // Filter & Search setup
  function setupFilters() {
    // Real-time Search
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderNews();
    });

    // Language Filter Buttons
    filterBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        filterBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentFilter = btn.getAttribute("data-lang");
        renderNews();
      });
    });
  }

  // Fetch Data (News & Resources)
  async function fetchData() {
    try {
      // Fetch news and resources in parallel
      const [newsRes, resourcesRes] = await Promise.all([
        fetch("./data/news.json").then(res => {
          if (!res.ok) throw new Error("Failed to load news");
          return res.json();
        }),
        fetch("./data/resources.json").then(res => {
          if (!res.ok) throw new Error("Failed to load resources");
          return res.json();
        })
      ]);

      newsData = newsRes;
      resourcesData = resourcesRes;

      renderNews();
      renderResources();
    } catch (error) {
      console.error("Error loading data:", error);
      renderError();
    }
  }

  // Render News list
  function renderNews() {
    // Filter news based on query and language filter
    const filteredNews = newsData.filter(item => {
      const matchesSearch = 
        item.title.toLowerCase().includes(searchQuery) || 
        item.source.toLowerCase().includes(searchQuery);
      
      const matchesLang = currentFilter === "all" || item.lang === currentFilter;
      
      return matchesSearch && matchesLang;
    });

    if (filteredNews.length === 0) {
      newsGrid.innerHTML = `
        <div class="loading-spinner" style="grid-column: 1 / -1;">
          <p style="font-size: 1.2rem; color: var(--text-secondary);">검색 결과에 맞는 뉴스가 없습니다.</p>
        </div>
      `;
      return;
    }

    newsGrid.innerHTML = filteredNews.map(item => {
      const badgeClass = item.lang === "ko" ? "badge-ko" : "badge-en";
      const badgeText = item.lang === "ko" ? "KR" : "EN";
      
      // Translation tip for English articles instead of broken links
      let translateTipHtml = "";
      if (item.lang === "en") {
        translateTipHtml = `
          <div class="card-translate-tip">
            <span>💡 <b>번역 팁:</b> 마우스 우클릭 후 <b>'한국어로 번역'</b>을 사용해보세요.</span>
          </div>
        `;
      }

      return `
        <article class="card">
          <div class="card-meta">
            <span class="badge ${badgeClass}">${badgeText}</span>
            <span class="card-source">${escapeHtml(item.source)}</span>
          </div>
          <h3 class="card-title">
            <a href="${item.link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;">
              ${escapeHtml(item.title)}
            </a>
          </h3>
          <div class="card-meta" style="margin-bottom: 0.5rem;">
            <span class="card-date">${item.displayDate}</span>
          </div>
          ${translateTipHtml}
          <div class="card-actions">
            <a class="card-link-btn" href="${item.link}" target="_blank" rel="noopener noreferrer">
              원문 읽기
              <svg class="card-link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </a>
          </div>
        </article>
      `;
    }).join("");
  }

  // Render Resources section
  function renderResources() {
    if (!resourcesData || resourcesData.length === 0) {
      resourcesContainer.innerHTML = `<p>등록된 공부 자료가 없습니다.</p>`;
      return;
    }

    resourcesContainer.innerHTML = resourcesData.map(cat => {
      const itemsHtml = cat.items.map(item => `
        <div class="resource-card">
          <a class="resource-title" href="${item.url}" target="_blank" rel="noopener noreferrer">
            ${escapeHtml(item.title)}
          </a>
          <p class="resource-desc">${escapeHtml(item.description)}</p>
        </div>
      `).join("");

      return `
        <section class="resource-category-section">
          <h2 class="category-title">${escapeHtml(cat.category)}</h2>
          <div class="resource-cards-list">
            ${itemsHtml}
          </div>
        </section>
      `;
    }).join("");
  }

  // Render Error UI if fetch fails
  function renderError() {
    const errorHtml = `
      <div class="loading-spinner" style="grid-column: 1 / -1;">
        <span style="font-size: 2rem;">⚠️</span>
        <p style="font-size: 1.1rem; color: #ef4444; font-weight: 500;">데이터를 불러오는 중 오류가 발생했습니다.</p>
        <p style="font-size: 0.9rem; color: var(--text-secondary);">GitHub Actions가 아직 최초 뉴스 수집을 완료하지 않았거나 파일 경로에 문제가 있을 수 있습니다.</p>
      </div>
    `;
    newsGrid.innerHTML = errorHtml;
    resourcesContainer.innerHTML = errorHtml;
  }

  // Helper to escape HTML tags to prevent XSS
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
