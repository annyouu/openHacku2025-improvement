// グローバルカウンタ（追加されたフォームに一意の index を付与）
let mealCount = 0;

function displayFileName(input) {
    let fileNameSpan = document.getElementById(input.id + "-name");
    if (input.files.length > 0) {
        fileNameSpan.textContent = input.files[0].name;
    } else {
        fileNameSpan.textContent = "選択されていません";
    }
}

// 初期の file-input に対してイベント登録
document.querySelectorAll('.file-input').forEach(input => {
    input.addEventListener('change', function () {
        displayFileName(this);
    });
});

// モーダル表示・非表示
function showModal() {
    document.getElementById('modalOverlay').style.display = 'block';
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = "none";
}

// ページ読み込み時に保存されたフォームを復元
document.addEventListener('DOMContentLoaded', function () {
    loadForms();
});

function registerModal() {
    let foodName = document.getElementById('modalFoodName').value.trim();

    if (foodName) {
        mealCount++;  // 新たなフォームには一意の番号を付与
        let newForm = createForm(foodName, mealCount);
        // フォーム内の追加食事入力エリアに挿入
        document.querySelector('form').insertBefore(newForm, document.querySelector('.add-form-btn'));

        // ローカルストレージへ保存
        saveForm({ foodName: foodName, index: mealCount });

        // モーダルを閉じ、入力をリセット
        closeModal();
        document.getElementById('modalFoodName').value = '';
    } else {
        alert('食事名を入力してください');
    }
}

// 食事名とファイル入力のフォームを生成
function createForm(foodName, index) {
    let newForm = document.createElement('div');
    newForm.classList.add('form-container');
    newForm.dataset.foodIndex = index;  // 後で削除するための識別用

    // 表示用の見出し（食事名）
    let newHeading = document.createElement('h3');
    newHeading.textContent = foodName;

    // サーバーへ送信するための hidden input (name: meal_name_{index})
    let hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'meal_name_' + index;
    hiddenInput.value = foodName;

    // ファイル選択用のラベル
    let newLabel = document.createElement('label');
    newLabel.setAttribute('for', 'meal_file_' + index);
    newLabel.classList.add('file-label');
    newLabel.textContent = foodName + "の写真を撮る";

    // ファイル入力（name: meal_file_{index}）
    let newFileInput = document.createElement('input');
    newFileInput.type = 'file';
    newFileInput.id = 'meal_file_' + index;
    newFileInput.name = 'meal_file_' + index;
    newFileInput.accept = 'image/*';
    newFileInput.classList.add('file-input');

    // ファイル名表示用の span
    let newFileNameSpan = document.createElement('span');
    newFileNameSpan.id = 'meal_file_' + index + '-name';
    newFileNameSpan.classList.add('file-name');
    newFileNameSpan.textContent = "選択されていません";

    // 削除ボタン
    let deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.textContent = "削除";
    deleteButton.classList.add('delete-btn');
    deleteButton.addEventListener('click', function () {
        removeForm(index);
    });

    // 各要素の追加
    newForm.appendChild(newHeading);
    newForm.appendChild(hiddenInput);
    newForm.appendChild(newLabel);
    newForm.appendChild(newFileInput);
    newForm.appendChild(newFileNameSpan);
    newForm.appendChild(deleteButton);

    // ファイル入力変更時のイベント登録
    newFileInput.addEventListener('change', function () {
        displayFileName(this);
    });

    return newForm;
}

// フォーム情報をローカルストレージに保存
function saveForm(formData) {
    let savedForms = JSON.parse(localStorage.getItem('savedForms')) || [];
    savedForms.push(formData);
    localStorage.setItem('savedForms', JSON.stringify(savedForms));
}

// 指定した index のフォームを削除
function removeForm(index) {
    let formToRemove = document.querySelector(`.form-container[data-food-index="${index}"]`);
    if (formToRemove) {
        formToRemove.remove();
    }
    let savedForms = JSON.parse(localStorage.getItem('savedForms')) || [];
    savedForms = savedForms.filter(item => item.index != index);
    localStorage.setItem('savedForms', JSON.stringify(savedForms));
}

// ローカルストレージから保存されたフォームを復元
function loadForms() {
    let savedForms = JSON.parse(localStorage.getItem('savedForms')) || [];
    savedForms.forEach(item => {
        // グローバルカウンタを最新の index に合わせる
        if (item.index > mealCount) {
            mealCount = item.index;
        }
        let newForm = createForm(item.foodName, item.index);
        document.querySelector('form').insertBefore(newForm, document.querySelector('.add-form-btn'));
    });
}
