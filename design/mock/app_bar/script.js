// App Bar インタラクション処理

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
  projectDropdown.classList.remove('active');
  projectSelectorBtn.classList.remove('active');
  notificationDropdown.classList.remove('active');
  settingsDropdown.classList.remove('active');
  accountDropdown.classList.remove('active');
}

// ハンバーガーメニューを閉じる関数
function closeHamburgerMenu() {
  hamburgerMenu.classList.remove('active');
  overlay.classList.remove('active');
}

// オーバーレイを表示する関数
function showOverlay() {
  overlay.classList.add('active');
}

// オーバーレイを非表示にする関数
function hideOverlay() {
  overlay.classList.remove('active');
}

// ハンバーガーメニューのトグル
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

// プロジェクト選択のトグル
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
    setTimeout(() => projectSearch.focus(), 100);
  }
});

// 通知のトグル
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

// 設定のトグル
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

// アカウントのトグル
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

// オーバーレイクリックで全て閉じる
overlay.addEventListener('click', () => {
  closeAllDropdowns();
  closeHamburgerMenu();
});

// ドロップダウン内のクリックで閉じないようにする
projectDropdown.addEventListener('click', (e) => {
  e.stopPropagation();
});

notificationDropdown.addEventListener('click', (e) => {
  e.stopPropagation();
});

settingsDropdown.addEventListener('click', (e) => {
  e.stopPropagation();
});

accountDropdown.addEventListener('click', (e) => {
  e.stopPropagation();
});

hamburgerMenu.addEventListener('click', (e) => {
  e.stopPropagation();
});

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
    document.querySelector('.project-name').textContent = projectName;
    
    // ドロップダウンを閉じる
    projectDropdown.classList.remove('active');
    projectSelectorBtn.classList.remove('active');
    hideOverlay();
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

// タブ切り替え機能
const dropdownTabs = document.querySelectorAll('.dropdown-tab');
dropdownTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    dropdownTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    
    // 実際の実装では、ここでプロジェクトリストをフィルタリングします
    console.log('タブ切り替え:', tab.textContent);
  });
});

console.log('App Bar initialized successfully!');

