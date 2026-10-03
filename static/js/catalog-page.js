let currentView = 'grid';
let currentSortField = 'title';
let currentSortOrder = 'desc';

let main_category_slug = '';
let category_slug = '';
let csrfToken = '';

function loadView() {
  const url = `/catalog/${main_category_slug}/${category_slug}/${currentView}/?sort_field=${currentSortField}&sort_order=${currentSortOrder}`;
  fetch(url)
    .then(response => response.text())
    .then(html => {
      document.getElementById('productContainer').innerHTML = html;
      updateViewButtons();
      updateSortButtons();
    });
}

function switchView(view) {
  currentView = view;
  updateViewButtons();
  loadView();
}

function changeSort(field) {
  if (currentSortField === field) {
    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
  } else {
    currentSortField = field;
    currentSortOrder = 'asc';
  }
  updateSortButtons();
  loadView();
}

function updateSortButtons() {
  const sortTitleBtn = document.getElementById('sortTitle');
  const sortPriceBtn = document.getElementById('sortPrice');
  const iconTitle = document.getElementById('iconTitle');
  const iconPrice = document.getElementById('iconPrice');

  sortTitleBtn.classList.remove('is-active');
  sortPriceBtn.classList.remove('is-active');
  iconTitle.className = 'fas';
  iconPrice.className = 'fas';

  if (currentSortField === 'title') {
    sortTitleBtn.classList.add('is-active');
    iconTitle.classList.add(currentSortOrder === 'asc' ? 'fa-arrow-up' : 'fa-arrow-down');
  } else if (currentSortField === 'price') {
    sortPriceBtn.classList.add('is-active');
    iconPrice.classList.add(currentSortOrder === 'asc' ? 'fa-arrow-up' : 'fa-arrow-down');
  }
}

function updateViewButtons() {
  document.getElementById('btnGrid').classList.toggle('is-active', currentView === 'grid');
  document.getElementById('btnList').classList.toggle('is-active', currentView === 'list');
}

document.addEventListener('DOMContentLoaded', () => {
  // Получение переменных из data-атрибутов
  const el = document.getElementById('productapp');
  category_slug = el.dataset.slug;
  main_category_slug = el.dataset.mainSlug;
  csrfToken = el.dataset.csrf;

  updateSortButtons();
  updateViewButtons();
  loadView();
});
