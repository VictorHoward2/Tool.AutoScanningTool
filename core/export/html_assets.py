CSS_TEMPLATE = """
    body {
        font-family: "Inter", "Segoe UI", sans-serif;
        background: #f5f6fa;
        margin: 0;
        padding: 20px;
        color: #333;
        background-image: url("https://raw.githubusercontent.com/VictorHoward2/Tool.AutoScanningTool/refs/heads/main/ui/assets/News.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    header {
        max-width: 800px;
        margin: auto;
        padding: 20px 0;
        text-align: center;
    }
    header h1 { margin: 0; font-size: 2rem; }
    header p { color: #666; }
    main {
        max-width: 800px;
        margin: auto;
        display: grid;
        gap: 20px;
    }
    article {
        background: #fff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    article:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    article h2 {
        margin-top: 0;
        font-size: 1.25rem;
    }
    article h2 a {
        color: #1a73e8;
        text-decoration: none;
    }
    article h2 a:hover {
        text-decoration: underline;
    }
    .meta {
        font-size: 0.875rem;
        color: #999;
        margin-bottom: 10px;
    }
    .snippet {
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .translation-label {
        font-size: 0.9rem;
        font-style: italic;
        color: #555;
        margin-top: 12px;
        margin-bottom: 4px;
    }
    .translation {
        background: #f9f9f9;
        padding: 12px;
        border-left: 4px solid #1a73e8;
        border-radius: 6px;
        line-height: 1.6;
        font-style: italic;
        color: #444;
        white-space: pre-wrap;
    }
    .category-tags {
        margin-bottom: 12px;
    }
    .tag {
        display: inline-block;
        background: #e8f0fe;
        color: #1967d2;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    .filter-bar {
        text-align: center;
        max-width: 800px;
        margin: auto;
        padding: 25px;
    }
    .filter-btn {
        background: #e0e0e0;
        border: none;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .filter-btn.active, .filter-btn:hover {
        background: #1a73e8;
        color: #fff;
    }
    .lang-switcher {
        text-align: center;
        margin-bottom: 12px;
    }

    .lang-switcher .filter-btn {
        padding: 10px 10px;
        font-size: 12px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        border-radius: 8px;
        margin: 0 5px;
        background: #f0f0f0;
        color: #333;
        transition: all 0.25s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }

    .lang-switcher .filter-btn:hover {
        background: #e5e5e5;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }

    .lang-switcher .filter-btn.active {
        background: #0078ff;
        color: white;
        box-shadow: 0 3px 6px rgba(0,120,255,0.3);
    }

    .lang-switcher .filter-btn.active:hover {
        background: #0069e0;
    }

    .article-actions {
        display: flex;
        gap: 8px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #e0e0e0;
    }
    .action-btn {
        padding: 6px 12px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: all 0.2s;
        font-weight: 500;
    }
    .btn-edit {
        background: #34a853;
        color: white;
    }
    .btn-edit:hover {
        background: #2d8f47;
    }
    .btn-delete {
        background: #ea4335;
        color: white;
    }
    .btn-delete:hover {
        background: #c5221f;
    }
    .btn-save {
        background: #1a73e8;
        color: white;
    }
    .btn-save:hover {
        background: #1557b0;
    }
    .btn-cancel {
        background: #9aa0a6;
        color: white;
    }
    .btn-cancel:hover {
        background: #80868b;
    }
    .add-article-btn {
        max-width: 800px;
        margin: 20px auto;
        text-align: center;
    }
    .add-article-btn button {
        background: #1a73e8;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 600;
    }
    .add-article-btn button:hover {
        background: #1557b0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .edit-form {
        display: none;
        margin-top: 15px;
        padding: 15px;
        background: #f9f9f9;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .edit-form.active {
        display: block;
    }
    .edit-form label {
        display: block;
        margin-top: 10px;
        margin-bottom: 5px;
        font-weight: 600;
        color: #333;
        font-size: 0.9rem;
    }
    .edit-form input,
    .edit-form textarea {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 0.9rem;
        font-family: inherit;
        box-sizing: border-box;
    }
    .edit-form textarea {
        min-height: 80px;
        resize: vertical;
    }
    .article-content {
        position: relative;
    }
    .article-content.editing .article-display {
        display: none;
    }
    .article-content.editing .edit-form {
        display: block;
    }

"""

JS_TEMPLATE = """
    function filterArticles(category) {
        const articles = document.querySelectorAll('article');
        const buttons = document.querySelectorAll('.filter-btn');

        // Reset trạng thái nút
        buttons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(category).classList.add('active');

        // Lọc bài viết
        articles.forEach(article => {
            const categories = article.dataset.categories || ''; // tránh lỗi undefined
            if (category === 'all' || categories.includes(category)) {
                article.style.display = 'block';
            } else {
                article.style.display = 'none';
            }
        });
    }
"""

LANG_SWITCHER_JS = """
    function switchLanguage(lang) {
        const viElems = document.querySelectorAll('.lang-vi');
        const enElems = document.querySelectorAll('.lang-en');
        const viBtn = document.getElementById('lang-vi-btn');
        const enBtn = document.getElementById('lang-en-btn');

        if (lang === 'vi') {
            viElems.forEach(e => e.style.display = '');
            enElems.forEach(e => e.style.display = 'none');
            viBtn.classList.add('active');
            enBtn.classList.remove('active');
        } else {
            viElems.forEach(e => e.style.display = 'none');
            enElems.forEach(e => e.style.display = '');
            enBtn.classList.add('active');
            viBtn.classList.remove('active');
        }
    }
"""

CRUD_JS = """
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    let articleCounter = 0;

    function updateArticleNumbers() {
        const articles = document.querySelectorAll('main > article:not(.new-article-form)');
        articles.forEach((article, index) => {
            const number = index;
            const h2Vi = article.querySelector('.lang-vi h2');
            const h2En = article.querySelector('.lang-en h2');
            if (h2Vi) {
                const titleMatch = h2Vi.textContent.match(/^\\d+\\.\\s*(.+)$/);
                if (titleMatch) {
                    const title = titleMatch[1].replace(/<[^>]*>/g, '').trim();
                    const link = h2Vi.querySelector('a');
                    if (link) {
                        const linkHref = escapeHtml(link.href);
                        const titleEscaped = escapeHtml(title);
                        h2Vi.innerHTML = number + '. <a href="' + linkHref + '">' + titleEscaped + '</a>';
                    } else {
                        h2Vi.textContent = number + '. ' + title;
                    }
                }
            }
            if (h2En) {
                const titleMatch = h2En.textContent.match(/^\\d+\\.\\s*(.+)$/);
                if (titleMatch) {
                    const title = titleMatch[1].replace(/<[^>]*>/g, '').trim();
                    const link = h2En.querySelector('a');
                    if (link) {
                        const linkHref = escapeHtml(link.href);
                        const titleEscaped = escapeHtml(title);
                        h2En.innerHTML = number + '. <a href="' + linkHref + '">' + titleEscaped + '</a>';
                    } else {
                        h2En.textContent = number + '. ' + title;
                    }
                }
            }
        });
    }

    function editArticle(articleElement) {
        const articleContent = articleElement.querySelector('.article-content');
        if (!articleContent) return;

        const langVi = articleContent.querySelector('.lang-vi');
        const langEn = articleContent.querySelector('.lang-en');

        // Extract data
        const h2Vi = langVi.querySelector('h2');
        const h2En = langEn.querySelector('h2');
        const titleVi = h2Vi ? h2Vi.textContent.replace(/^\\d+\\.\\s*/, '').trim() : '';
        const titleEn = h2En ? h2En.textContent.replace(/^\\d+\\.\\s*/, '').trim() : '';
        const linkEl = h2Vi?.querySelector('a') || h2En?.querySelector('a');
        const link = linkEl ? linkEl.href : '';
        const published = langVi.querySelector('.meta')?.textContent.trim() || '';
        const snippet = langVi.querySelector('.snippet')?.textContent.trim() || '';

        // Find translation sections
        let vietsub = '';
        let summaryVi = '';
        let summaryEn = '';
        let related = '';
        let extract = '';

        const labelsVi = langVi.querySelectorAll('.translation-label');
        labelsVi.forEach(label => {
            const text = label.textContent.trim();
            const next = label.nextElementSibling;
            if (next && next.classList.contains('translation')) {
                if (text.includes('Dịch')) {
                    vietsub = next.textContent.trim();
                } else if (text.includes('Tóm tắt')) {
                    summaryVi = next.textContent.trim();
                } else if (text.includes('liên quan')) {
                    related = next.textContent.trim();
                } else if (text.includes('thông tin')) {
                    extract = next.textContent.trim();
                }
            }
        });

        const labelsEn = langEn.querySelectorAll('.translation-label');
        labelsEn.forEach(label => {
            const text = label.textContent.trim();
            const next = label.nextElementSibling;
            if (next && next.classList.contains('translation')) {
                if (text.includes('Summary')) {
                    summaryEn = next.textContent.trim();
                } else if (text.includes('Related')) {
                    related = related || next.textContent.trim();
                } else if (text.includes('Useful')) {
                    extract = extract || next.textContent.trim();
                }
            }
        });

        // Create form HTML
        const formHtml = `
            <div class="edit-form active">
                <label>Tiêu đề (VI):</label>
                <input type="text" id="edit-title-vi" value="${escapeHtml(titleVi)}">
                <label>Title (EN):</label>
                <input type="text" id="edit-title-en" value="${escapeHtml(titleEn)}">
                <label>Link:</label>
                <input type="text" id="edit-link" value="${escapeHtml(link)}">
                <label>Published:</label>
                <input type="text" id="edit-published" value="${escapeHtml(published)}">
                <label>Snippet:</label>
                <textarea id="edit-snippet">${escapeHtml(snippet)}</textarea>
                <label>Dịch tiếng Việt:</label>
                <textarea id="edit-vietsub">${escapeHtml(vietsub)}</textarea>
                <label>Tóm tắt (VI):</label>
                <textarea id="edit-summary-vi">${escapeHtml(summaryVi)}</textarea>
                <label>Summary (EN):</label>
                <textarea id="edit-summary-en">${escapeHtml(summaryEn)}</textarea>
                <label>Có liên quan:</label>
                <textarea id="edit-related">${escapeHtml(related)}</textarea>
                <label>Thông tin hữu ích:</label>
                <textarea id="edit-extract">${escapeHtml(extract)}</textarea>
                <div class="article-actions">
                    <button class="action-btn btn-save" onclick="saveArticle(this)">Lưu</button>
                    <button class="action-btn btn-cancel" onclick="cancelEdit(this)">Hủy</button>
                </div>
            </div>
        `;

        articleContent.classList.add('editing');
        const existingForm = articleContent.querySelector('.edit-form');
        if (existingForm) {
            existingForm.remove();
        }
        articleContent.insertAdjacentHTML('beforeend', formHtml);
    }

    function saveArticle(btn) {
        const form = btn.closest('.edit-form');
        const article = btn.closest('article');
        const articleContent = article.querySelector('.article-content');

        const titleVi = document.getElementById('edit-title-vi').value.trim();
        const titleEn = document.getElementById('edit-title-en').value.trim();
        const link = document.getElementById('edit-link').value.trim();
        const published = document.getElementById('edit-published').value.trim();
        const snippet = document.getElementById('edit-snippet').value.trim();
        const vietsub = document.getElementById('edit-vietsub').value.trim();
        const summaryVi = document.getElementById('edit-summary-vi').value.trim();
        const summaryEn = document.getElementById('edit-summary-en').value.trim();
        const related = document.getElementById('edit-related').value.trim();
        const extract = document.getElementById('edit-extract').value.trim();

        const currentNumber = article.querySelector('.lang-vi h2')?.textContent.match(/^(\\d+)\\./)?.[1] || '';

        // Escape HTML for safety
        const titleViEscaped = escapeHtml(titleVi || titleEn || 'No Title');
        const titleEnEscaped = escapeHtml(titleEn || titleVi || 'No Title');
        const linkEscaped = escapeHtml(link);
        const publishedEscaped = escapeHtml(published);
        const snippetEscaped = escapeHtml(snippet).replace(/\\n/g, '<br>');
        const vietsubEscaped = escapeHtml(vietsub).replace(/\\n/g, '<br>');
        const summaryViEscaped = escapeHtml(summaryVi).replace(/\\n/g, '<br>');
        const summaryEnEscaped = escapeHtml(summaryEn).replace(/\\n/g, '<br>');
        const relatedEscaped = escapeHtml(related).replace(/\\n/g, '<br>');
        const extractEscaped = escapeHtml(extract).replace(/\\n/g, '<br>');

        const titleHtmlVi = link ? `<a href="${linkEscaped}">${titleViEscaped}</a>` : titleViEscaped;
        const titleHtmlEn = link ? `<a href="${linkEscaped}">${titleEnEscaped}</a>` : titleEnEscaped;

        const langViHtml = `
            <div class="lang-vi">
                <h2>${currentNumber}. ${titleHtmlVi}</h2>
                <div class="meta">${publishedEscaped}</div>
                <p class="snippet">${snippetEscaped}</p>
                ${vietsub ? `<p class="translation-label">Dịch tiếng Việt:</p><p class="translation">${vietsubEscaped}</p>` : ''}
                ${summaryVi ? `<p class="translation-label">Tóm tắt:</p><p class="translation">${summaryViEscaped}</p>` : ''}
                ${related ? `<p class="translation-label">Có liên quan đến chủ đề:</p><p class="translation">${relatedEscaped}</p>` : ''}
                ${extract ? `<p class="translation-label">Các thông tin hữu ích:</p><p class="translation">${extractEscaped}</p>` : ''}
            </div>
        `;

        const langEnHtml = `
            <div class="lang-en" style="display:none">
                <h2>${currentNumber}. ${titleHtmlEn}</h2>
                <div class="meta">${publishedEscaped}</div>
                <p class="snippet">${snippetEscaped}</p>
                ${summaryEn ? `<p class="translation-label">Summary:</p><p class="translation">${summaryEnEscaped}</p>` : ''}
                ${related ? `<p class="translation-label">Related to topic:</p><p class="translation">${relatedEscaped}</p>` : ''}
                ${extract ? `<p class="translation-label">Useful info:</p><p class="translation">${extractEscaped}</p>` : ''}
            </div>
        `;

        const articleDisplay = articleContent.querySelector('.article-display');
        if (articleDisplay) {
            articleDisplay.innerHTML = langViHtml + langEnHtml;
        }

        articleContent.classList.remove('editing');
        form.remove();

        // Re-apply current language
        const currentLang = document.getElementById('lang-vi-btn').classList.contains('active') ? 'vi' : 'en';
        switchLanguage(currentLang);
    }

    function cancelEdit(btn) {
        const form = btn.closest('.edit-form');
        const articleContent = btn.closest('.article-content');
        articleContent.classList.remove('editing');
        form.remove();
    }

    function deleteArticle(articleElement) {
        if (confirm('Bạn có chắc chắn muốn xóa bài báo này?')) {
            articleElement.remove();
            updateArticleNumbers();
        }
    }

    function showAddArticleForm() {
        const main = document.querySelector('main');
        const existingForm = document.querySelector('.new-article-form');
        if (existingForm) {
            existingForm.remove();
            return;
        }

        const formHtml = `
            <article class="new-article-form" style="background: #fff3cd; border: 2px dashed #ffc107;">
                <div class="edit-form active">
                    <h3 style="margin-top: 0;">Thêm bài báo mới / Add New Article</h3>
                    <label>Tiêu đề (VI):</label>
                    <input type="text" id="new-title-vi" placeholder="Nhập tiêu đề tiếng Việt">
                    <label>Title (EN):</label>
                    <input type="text" id="new-title-en" placeholder="Enter English title">
                    <label>Link:</label>
                    <input type="text" id="new-link" placeholder="https://...">
                    <label>Published:</label>
                    <input type="text" id="new-published" placeholder="Ngày tháng">
                    <label>Snippet:</label>
                    <textarea id="new-snippet" placeholder="Nội dung tóm tắt"></textarea>
                    <label>Dịch tiếng Việt:</label>
                    <textarea id="new-vietsub" placeholder="Bản dịch tiếng Việt"></textarea>
                    <label>Tóm tắt (VI):</label>
                    <textarea id="new-summary-vi" placeholder="Tóm tắt tiếng Việt"></textarea>
                    <label>Summary (EN):</label>
                    <textarea id="new-summary-en" placeholder="English summary"></textarea>
                    <label>Có liên quan:</label>
                    <textarea id="new-related" placeholder="Thông tin liên quan"></textarea>
                    <label>Thông tin hữu ích:</label>
                    <textarea id="new-extract" placeholder="Thông tin hữu ích"></textarea>
                    <div class="article-actions">
                        <button class="action-btn btn-save" onclick="addArticle()">Thêm</button>
                        <button class="action-btn btn-cancel" onclick="showAddArticleForm()">Hủy</button>
                    </div>
                </div>
            </article>
        `;

        const overview = main.querySelector('article.translation-label');
        if (overview) {
            overview.insertAdjacentHTML('afterend', formHtml);
        } else {
            main.insertAdjacentHTML('afterbegin', formHtml);
        }
    }

    function addArticle() {
        const titleVi = document.getElementById('new-title-vi').value.trim();
        const titleEn = document.getElementById('new-title-en').value.trim();
        const link = document.getElementById('new-link').value.trim();
        const published = document.getElementById('new-published').value.trim();
        const snippet = document.getElementById('new-snippet').value.trim();
        const vietsub = document.getElementById('new-vietsub').value.trim();
        const summaryVi = document.getElementById('new-summary-vi').value.trim();
        const summaryEn = document.getElementById('new-summary-en').value.trim();
        const related = document.getElementById('new-related').value.trim();
        const extract = document.getElementById('new-extract').value.trim();

        if (!titleVi && !titleEn) {
            alert('Vui lòng nhập ít nhất một tiêu đề');
            return;
        }

        const articles = document.querySelectorAll('main > article:not(.new-article-form)');
        const nextNumber = articles.length + 1;

        // Escape HTML for safety
        const titleViEscaped = escapeHtml(titleVi || titleEn || 'No Title');
        const titleEnEscaped = escapeHtml(titleEn || titleVi || 'No Title');
        const linkEscaped = escapeHtml(link);
        const publishedEscaped = escapeHtml(published);
        const snippetEscaped = escapeHtml(snippet).replace(/\\n/g, '<br>');
        const vietsubEscaped = escapeHtml(vietsub).replace(/\\n/g, '<br>');
        const summaryViEscaped = escapeHtml(summaryVi).replace(/\\n/g, '<br>');
        const summaryEnEscaped = escapeHtml(summaryEn).replace(/\\n/g, '<br>');
        const relatedEscaped = escapeHtml(related).replace(/\\n/g, '<br>');
        const extractEscaped = escapeHtml(extract).replace(/\\n/g, '<br>');

        const titleHtmlVi = link ? `<a href="${linkEscaped}">${titleViEscaped}</a>` : titleViEscaped;
        const titleHtmlEn = link ? `<a href="${linkEscaped}">${titleEnEscaped}</a>` : titleEnEscaped;

        const langViHtml = `
            <div class="lang-vi">
                <h2>${nextNumber}. ${titleHtmlVi}</h2>
                ${publishedEscaped ? `<div class="meta">${publishedEscaped}</div>` : ''}
                ${snippetEscaped ? `<p class="snippet">${snippetEscaped}</p>` : ''}
                ${vietsubEscaped ? `<p class="translation-label">Dịch tiếng Việt:</p><p class="translation">${vietsubEscaped}</p>` : ''}
                ${summaryViEscaped ? `<p class="translation-label">Tóm tắt:</p><p class="translation">${summaryViEscaped}</p>` : ''}
                ${relatedEscaped ? `<p class="translation-label">Có liên quan đến chủ đề:</p><p class="translation">${relatedEscaped}</p>` : ''}
                ${extractEscaped ? `<p class="translation-label">Các thông tin hữu ích:</p><p class="translation">${extractEscaped}</p>` : ''}
            </div>
        `;

        const langEnHtml = `
            <div class="lang-en" style="display:none">
                <h2>${nextNumber}. ${titleHtmlEn}</h2>
                ${publishedEscaped ? `<div class="meta">${publishedEscaped}</div>` : ''}
                ${snippetEscaped ? `<p class="snippet">${snippetEscaped}</p>` : ''}
                ${summaryEnEscaped ? `<p class="translation-label">Summary:</p><p class="translation">${summaryEnEscaped}</p>` : ''}
                ${relatedEscaped ? `<p class="translation-label">Related to topic:</p><p class="translation">${relatedEscaped}</p>` : ''}
                ${extractEscaped ? `<p class="translation-label">Useful info:</p><p class="translation">${extractEscaped}</p>` : ''}
            </div>
        `;

        const articleHtml = `
            <article data-categories="">
                <div class="category-tags"></div>
                <div class="article-content">
                    <div class="article-display">
                        ${langViHtml}
                        ${langEnHtml}
                    </div>
                </div>
                <div class="article-actions">
                    <button class="action-btn btn-edit" onclick="editArticle(this.closest('article'))">Sửa</button>
                    <button class="action-btn btn-delete" onclick="deleteArticle(this.closest('article'))">Xóa</button>
                </div>
            </article>
        `;

        const main = document.querySelector('main');
        const newForm = document.querySelector('.new-article-form');
        if (newForm) {
            newForm.insertAdjacentHTML('afterend', articleHtml);
            newForm.remove();
        } else {
            main.insertAdjacentHTML('beforeend', articleHtml);
        }

        updateArticleNumbers();

        // Re-apply current language
        const currentLang = document.getElementById('lang-vi-btn').classList.contains('active') ? 'vi' : 'en';
        switchLanguage(currentLang);
    }

    // Initialize article numbers on load
    document.addEventListener('DOMContentLoaded', function() {
        updateArticleNumbers();
    });
"""
