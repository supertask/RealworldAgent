// RealworldAgent Frontend Mock - Common JavaScript
// Based on app_bar script.js with extensions

// ========== App Bar インタラクション (from app_bar) ==========

// DOM要素の取得
const hamburgerBtn = document.getElementById('hamburgerBtn');
const hamburgerMenu = document.getElementById('hamburgerMenu');
const projectSelectorBtn = document.getElementById('projectSelectorBtn');
const projectDropdown = document.getElementById('projectDropdown');
const notificationBtn = document.getElementById('notificationBtn');
const notificationDropdown = document.getElementById('notificationDropdown');
const settingsBtn = document.getElementById('settingsBtn');
const settingsDropdown = document.getElementById('settingsDropdown');
const accountBtn = document.getElementById('accountBtn');
const accountDropdown = document.getElementById('accountDropdown');
const overlay = document.getElementById('overlay');
const projectSearch = document.getElementById('projectSearch');

// 全てのドロップダウンを閉じる関数
function closeAllDropdowns() {
  if (projectDropdown) projectDropdown.classList.remove('active');
  if (projectSelectorBtn) projectSelectorBtn.classList.remove('active');
  if (notificationDropdown) notificationDropdown.classList.remove('active');
  if (settingsDropdown) settingsDropdown.classList.remove('active');
  if (accountDropdown) accountDropdown.classList.remove('active');
}

// ハンバーガーメニューを閉じる関数
function closeHamburgerMenu() {
  if (hamburgerMenu) hamburgerMenu.classList.remove('active');
  if (overlay) overlay.classList.remove('active');
}

// オーバーレイを表示する関数
function showOverlay() {
  if (overlay) overlay.classList.add('active');
}

// オーバーレイを非表示にする関数
function hideOverlay() {
  if (overlay) overlay.classList.remove('active');
}

// ハンバーガーメニューのトグル
if (hamburgerBtn) {
  hamburgerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeAllDropdowns();
    
    const isActive = hamburgerMenu.classList.contains('active');
    if (isActive) {
      closeHamburgerMenu();
    } else {
      hamburgerMenu.classList.add('active');
      showOverlay();
    }
  });
}

// プロジェクト選択のトグル
if (projectSelectorBtn) {
  projectSelectorBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeHamburgerMenu();
    
    const isActive = projectDropdown.classList.contains('active');
    if (isActive) {
      projectDropdown.classList.remove('active');
      projectSelectorBtn.classList.remove('active');
      hideOverlay();
    } else {
      closeAllDropdowns();
      projectDropdown.classList.add('active');
      projectSelectorBtn.classList.add('active');
      showOverlay();
      // フォーカスを検索ボックスに移動
      if (projectSearch) {
        setTimeout(() => projectSearch.focus(), 100);
      }
    }
  });
}

// 通知のトグル
if (notificationBtn) {
  notificationBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeHamburgerMenu();
    
    const isActive = notificationDropdown.classList.contains('active');
    if (isActive) {
      notificationDropdown.classList.remove('active');
      hideOverlay();
    } else {
      closeAllDropdowns();
      notificationDropdown.classList.add('active');
      showOverlay();
    }
  });
}

// 設定のトグル
if (settingsBtn) {
  settingsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeHamburgerMenu();
    
    const isActive = settingsDropdown.classList.contains('active');
    if (isActive) {
      settingsDropdown.classList.remove('active');
      hideOverlay();
    } else {
      closeAllDropdowns();
      settingsDropdown.classList.add('active');
      showOverlay();
    }
  });
}

// アカウントのトグル
if (accountBtn) {
  accountBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    closeHamburgerMenu();
    
    const isActive = accountDropdown.classList.contains('active');
    if (isActive) {
      accountDropdown.classList.remove('active');
      hideOverlay();
    } else {
      closeAllDropdowns();
      accountDropdown.classList.add('active');
      showOverlay();
    }
  });
}

// オーバーレイクリックで全て閉じる
if (overlay) {
  overlay.addEventListener('click', () => {
    closeAllDropdowns();
    closeHamburgerMenu();
  });
}

// ドロップダウン内のクリックで閉じないようにする
if (projectDropdown) {
  projectDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

if (notificationDropdown) {
  notificationDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

if (settingsDropdown) {
  settingsDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

if (accountDropdown) {
  accountDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

if (hamburgerMenu) {
  hamburgerMenu.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

// ドキュメント全体のクリックで閉じる
document.addEventListener('click', () => {
  closeAllDropdowns();
  closeHamburgerMenu();
});

// ESCキーで閉じる
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeAllDropdowns();
    closeHamburgerMenu();
  }
});

// プロジェクト選択の処理
const projectItems = document.querySelectorAll('.project-item');
projectItems.forEach(item => {
  item.addEventListener('click', (e) => {
    // スターボタンのクリックは除外
    if (e.target.closest('.project-item-star')) {
      return;
    }
    
    // 選択状態を更新
    projectItems.forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    
    // プロジェクト名を更新
    const projectName = item.querySelector('.project-item-name').textContent;
    const projectNameEl = document.querySelector('.project-name');
    if (projectNameEl) {
      projectNameEl.textContent = projectName;
    }
    
    // ドロップダウンを閉じる
    projectDropdown.classList.remove('active');
    projectSelectorBtn.classList.remove('active');
    hideOverlay();
    
    // ページをリロード（実際のアプリではプロジェクトIDでフィルタリング）
    const projectId = item.dataset.projectId;
    if (projectId) {
      localStorage.setItem('selectedProjectId', projectId);
      // ページに応じてコンテンツを更新
      if (typeof updatePageContent === 'function') {
        updatePageContent(projectId);
      }
    }
  });
});

// スターボタンの処理
const starButtons = document.querySelectorAll('.project-item-star');
starButtons.forEach(button => {
  button.addEventListener('click', (e) => {
    e.stopPropagation();
    
    // スター状態をトグル
    if (button.textContent === '☆') {
      button.textContent = '★';
      button.style.color = '#f9ab00';
    } else {
      button.textContent = '☆';
      button.style.color = '';
    }
  });
});

// プロジェクト検索機能
if (projectSearch) {
  projectSearch.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    
    projectItems.forEach(item => {
      const projectName = item.querySelector('.project-item-name').textContent.toLowerCase();
      const projectId = item.querySelector('.project-item-id').textContent.toLowerCase();
      
      if (projectName.includes(searchTerm) || projectId.includes(searchTerm)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });
}

// ========== 通知システム ==========

// 通知を読み込む
function loadNotifications() {
  const notificationContent = document.querySelector('.notification-content');
  if (!notificationContent) return;
  
  const unreadNotifications = MockDataHelpers.getUnreadNotifications();
  
  if (unreadNotifications.length === 0) {
    notificationContent.innerHTML = '<p class="notification-empty">通知はありません</p>';
    return;
  }
  
  notificationContent.innerHTML = mockNotifications.map(notif => `
    <div class="notification-item ${notif.read ? '' : 'unread'}" data-id="${notif.id}">
      <div class="notification-item-header">
        <div class="notification-item-title">${notif.title}</div>
        <div class="notification-item-time">${MockDataHelpers.formatRelativeTime(notif.timestamp)}</div>
      </div>
      <div class="notification-item-message">${notif.message}</div>
    </div>
  `).join('');
  
  // 通知クリックで対応ページへ遷移
  notificationContent.querySelectorAll('.notification-item').forEach(item => {
    item.addEventListener('click', () => {
      const notif = mockNotifications.find(n => n.id === item.dataset.id);
      if (notif && notif.link) {
        window.location.href = notif.link;
      }
    });
  });
  
  // バッジ更新
  updateNotificationBadge();
}

// 通知バッジを更新
function updateNotificationBadge() {
  const badge = document.querySelector('.notification-badge');
  if (!badge) return;
  
  const unreadCount = MockDataHelpers.getUnreadNotifications().length;
  if (unreadCount > 0) {
    badge.textContent = unreadCount;
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

// ========== プログレスバーアニメーション ==========

// プログレスバーをアニメーション
function animateProgressBar(element, targetValue, duration = 1000) {
  const fill = element.querySelector('.progress-bar-fill');
  const valueEl = element.querySelector('.progress-bar-value');
  
  if (!fill || !valueEl) return;
  
  let startValue = 0;
  const startTime = Date.now();
  
  function update() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const currentValue = Math.floor(startValue + (targetValue - startValue) * eased);
    
    fill.style.width = `${currentValue}%`;
    valueEl.textContent = `${currentValue}%`;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  requestAnimationFrame(update);
}

// ページ読み込み時にすべてのプログレスバーをアニメーション
function initProgressBars() {
  document.querySelectorAll('.progress-bar-container').forEach(container => {
    const targetValue = parseInt(container.dataset.progress || '0');
    animateProgressBar(container, targetValue);
  });
}

// ========== ステータス遷移アニメーション ==========

// ステータスバッジを更新（アニメーション付き）
function updateStatusBadge(element, newStatus) {
  const statusMap = {
    pending: { text: '待機中', class: 'status-badge-pending', dot: 'status-dot-pending' },
    processing: { text: '処理中', class: 'status-badge-processing', dot: 'status-dot-processing' },
    completed: { text: '完了', class: 'status-badge-completed', dot: 'status-dot-completed' },
    error: { text: 'エラー', class: 'status-badge-error', dot: 'status-dot-error' },
    active: { text: 'アクティブ', class: 'status-badge-active', dot: 'status-dot-active' },
    merged: { text: 'マージ済み', class: 'status-badge-merged', dot: 'status-dot-merged' },
    open: { text: 'オープン', class: 'status-badge-open', dot: 'status-dot-open' }
  };
  
  const status = statusMap[newStatus];
  if (!status) return;
  
  // 古いクラスを削除
  element.className = 'status-badge';
  
  // フェードアウト
  element.style.opacity = '0';
  
  setTimeout(() => {
    // 新しいクラスを追加
    element.classList.add(status.class);
    
    // ドットを更新
    const dot = element.querySelector('.status-dot');
    if (dot) {
      dot.className = 'status-dot';
      dot.classList.add(status.dot);
    }
    
    // テキストを更新
    const textNode = Array.from(element.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
    if (textNode) {
      textNode.textContent = status.text;
    }
    
    // フェードイン
    element.style.opacity = '1';
  }, 200);
}

// ========== ログビューアー ==========

// ログエントリーを追加（自動スクロール）
function appendLogEntry(logViewer, entry) {
  const logEntry = document.createElement('div');
  logEntry.className = 'log-entry';
  
  logEntry.innerHTML = `
    <span class="log-timestamp">${entry.timestamp}</span>
    <span class="log-level log-level-${entry.level}">[${entry.level.toUpperCase()}]</span>
    <span class="log-message">${entry.message}</span>
  `;
  
  logViewer.appendChild(logEntry);
  
  // 自動スクロール
  logViewer.scrollTop = logViewer.scrollHeight;
}

// ログストリームをシミュレート
function simulateLogStream(logViewer, logs, interval = 500) {
  let index = 0;
  
  const timer = setInterval(() => {
    if (index >= logs.length) {
      clearInterval(timer);
      return;
    }
    
    appendLogEntry(logViewer, logs[index]);
    index++;
  }, interval);
  
  return timer;
}

// ========== カウントアップアニメーション ==========

function animateCountUp(element, targetValue, duration = 1000) {
  const startValue = 0;
  const startTime = Date.now();
  
  function update() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const currentValue = Math.floor(startValue + (targetValue - startValue) * eased);
    
    element.textContent = currentValue;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  
  requestAnimationFrame(update);
}

// ========== ページナビゲーション ==========

// 現在のページを取得
function getCurrentPage() {
  const path = window.location.pathname;
  const filename = path.substring(path.lastIndexOf('/') + 1);
  return filename || 'dashboard.html';
}

// ハンバーガーメニューのアクティブ状態を更新
function updateMenuActiveState() {
  const currentPage = getCurrentPage();
  const menuItems = document.querySelectorAll('.hamburger-menu-item');
  
  menuItems.forEach(item => {
    const href = item.getAttribute('href');
    if (href && href.includes(currentPage)) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });
}

// ========== ユーティリティ関数 ==========

// URLパラメータを取得
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

// 日付フォーマット
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

// 時刻フォーマット
function formatTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

// ========== 初期化 ==========

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  // 通知を読み込む
  loadNotifications();
  
  // プログレスバーを初期化
  initProgressBars();
  
  // メニューのアクティブ状態を更新
  updateMenuActiveState();
  
  // 選択中のプロジェクトを復元
  const selectedProjectId = localStorage.getItem('selectedProjectId');
  if (selectedProjectId) {
    const projectItem = document.querySelector(`.project-item[data-project-id="${selectedProjectId}"]`);
    if (projectItem) {
      projectItems.forEach(i => i.classList.remove('active'));
      projectItem.classList.add('active');
      
      const projectName = projectItem.querySelector('.project-item-name').textContent;
      const projectNameEl = document.querySelector('.project-name');
      if (projectNameEl) {
        projectNameEl.textContent = projectName;
      }
    }
  }
  
  console.log('RealworldAgent Frontend Mock initialized!');
});

// ========== Scope関連の関数 ==========

// scopeでフィルタリング
function filterByScope(items, scope) {
  if (!scope || scope === 'all_scopes') return items;
  return items.filter(item => item.scope === scope);
}

// Meeting名をパース
function parseMeetingName(meetingName) {
  const parts = meetingName.split('_');
  return {
    projectName: parts[0],
    scope: parts[1],
    title: parts.slice(2).join('_')
  };
}

// scopeの表示名を取得
function getScopeDisplayName(scope) {
  const scopeNames = {
    'frontend': 'フロントエンド',
    'backend': 'バックエンド',
    'test': 'テスト',
    'all': '全体',
    'management': 'マネジメント'
  };
  return scopeNames[scope] || scope;
}

// scopeバッジHTMLを生成
function renderScopeBadge(scope) {
  const displayName = getScopeDisplayName(scope);
  return `<span class="scope-badge scope-badge-${scope}">${displayName}</span>`;
}

// scopeフィルタドロップダウンを生成
function renderScopeFilter(containerId, onChangeCallback) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const filterHTML = `
    <div class="filter-bar">
      <label for="scopeFilter">Scope:</label>
      <select id="scopeFilter" class="scope-filter">
        <option value="all_scopes">すべてのscope</option>
        <option value="frontend">フロントエンド</option>
        <option value="backend">バックエンド</option>
        <option value="test">テスト</option>
        <option value="all">全体</option>
        <option value="management">マネジメント</option>
      </select>
    </div>
  `;
  
  container.innerHTML = filterHTML;
  
  const selectElement = document.getElementById('scopeFilter');
  if (selectElement && onChangeCallback) {
    selectElement.addEventListener('change', (e) => {
      onChangeCallback(e.target.value);
    });
  }
}

// ========== Export for use in other scripts ==========
window.RWACommon = {
  animateProgressBar,
  updateStatusBadge,
  appendLogEntry,
  simulateLogStream,
  animateCountUp,
  getQueryParam,
  formatDate,
  formatTime,
  closeAllDropdowns,
  closeHamburgerMenu,
  filterByScope,
  parseMeetingName,
  getScopeDisplayName,
  renderScopeBadge,
  renderScopeFilter
};

