(function () {
  'use strict';

  var ADMIN_PASSWORD = 'huy.nq2';
  var STORAGE_PREFIX = 'si-report-edit::';
  var MODULE_KEYS = ['globalInformation', 'newFeatures', 'hotAndroidIssues', 'patentTrend'];

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function cleanDescription(raw) {
    if (raw == null) return '';
    var text = String(raw);
    text = text.replace(/<br\s*\/?>/gi, ' ');
    text = text.replace(/<\/p>/gi, ' ');
    text = text.replace(/<[^>]+>/g, ' ');
    text = text.replace(/\s+/g, ' ').trim();
    return text;
  }

  function formatPublished(iso) {
    if (!iso) return '';
    try {
      var d = new Date(iso);
      if (isNaN(d.getTime())) return escapeHtml(String(iso));
      return escapeHtml(d.toLocaleString());
    } catch (e) {
      return escapeHtml(String(iso));
    }
  }

  function dualText(vi, en, bilingual, defaultLang) {
    vi = vi == null ? '' : String(vi);
    en = en == null ? '' : String(en);
    if (!bilingual) {
      return escapeHtml(defaultLang === 'vi' ? vi : en);
    }
    var viHide = defaultLang === 'vi' ? '' : ' style="display:none"';
    var enHide = defaultLang === 'en' ? '' : ' style="display:none"';
    return (
      '<span class="lang-vi"' + viHide + '>' + escapeHtml(vi) + '</span>' +
      '<span class="lang-en"' + enHide + '>' + escapeHtml(en) + '</span>'
    );
  }

  function titleHtml(item, idx) {
    var t = escapeHtml(item.title || 'No Title');
    var link = (item.link || '').trim();
    if (link) {
      return idx + '. <a href="' + escapeHtml(link) + '" target="_blank" rel="noopener noreferrer">' + t + '</a>';
    }
    return idx + '. ' + t;
  }

  function itemTagsRaw(item) {
    var raw = item.tags;
    var tags = [];
    if (Array.isArray(raw)) {
      raw.forEach(function (tag) {
        var x = String(tag).trim();
        if (x) tags.push(x);
      });
    }
    return tags;
  }

  function itemTags(item, L, defaultLang) {
    var tags = itemTagsRaw(item);
    if (!tags.length) {
      var fb = L.security ? L.security[defaultLang] || L.security.vi : 'Security';
      tags = [fb];
    }
    return tags;
  }

  function tagsJsonAttr(item) {
    return escapeHtml(JSON.stringify(itemTagsRaw(item)));
  }

  function renderTagFilterShell(L, bilingual, defaultLang, elementId) {
    var F = L.filter_by_tag || { vi: 'Loc theo tag', en: 'Filter by tag' };
    var label = dualText(F.vi, F.en, bilingual, defaultLang);
    return (
      '<div class="report-tag-filter mb-6" id="' +
      escapeHtml(elementId) +
      '">' +
      '<div class="mb-2 text-xs font-bold text-[#414755] uppercase tracking-wider">' +
      label +
      '</div>' +
      '<div class="report-tag-filter-chips flex flex-wrap gap-2">' +
      '<div class="report-tag-filter-chips-primary contents"></div>' +
      '<div class="report-tag-filter-chips-extra contents hidden"></div>' +
      '</div>' +
      '<button type="button" class="report-tag-filter-toggle hidden text-sm font-semibold text-[#0052d1] mt-1 hover:underline cursor-pointer bg-transparent border-0 p-0 font-inherit" aria-expanded="false"></button>' +
      '</div>'
    );
  }

  function imageOrPlaceholder(item, cls, grad) {
    var url = (item.image || '').toString().trim();
    if (url) {
      return '<img src="' + escapeHtml(url) + '" alt="article image" class="' + cls + '"/>';
    }
    return '<div class="' + cls + ' ' + grad + '"></div>';
  }

  function renderOverviewBlock(ov, L, bilingual, defaultLang) {
    var vi = ov && ov.vi != null ? ov.vi : '';
    var en = ov && ov.en != null ? ov.en : '';
    var inner = dualText(vi, en, bilingual, defaultLang);
    if (!String(vi).trim() && !String(en).trim()) return '';
    var titleDual = dualText(L.overall.vi, L.overall.en, bilingual, defaultLang);
    return (
      '<article class="bg-white rounded-lg p-6 border border-[#e1e3e4]">' +
        '<div class="flex items-center gap-2 mb-2 text-[#0052d1] font-bold text-xs uppercase tracking-widest">' +
          '<span class="material-symbols-outlined text-base" style="font-variation-settings: \'FILL\' 1;">auto_stories</span>' +
          titleDual +
        '</div>' +
        '<p class="text-[#414755] leading-relaxed">' + inner + '</p>' +
      '</article>'
    );
  }

  function renderEmpty(L, bilingual, defaultLang) {
    return '<p class="text-[#414755] italic">' + dualText(L.no_data.vi, L.no_data.en, bilingual, defaultLang) + '</p>';
  }

  function renderGlobalInformation(data, L, bilingual, defaultLang) {
    if (!data || !data.length) return renderEmpty(L, bilingual, defaultLang);
    var cards = '';
    for (var i = 0; i < data.length; i++) {
      var item = data[i];
      var idx = i + 1;
      var published = formatPublished(item.published);
      var snippet = escapeHtml(cleanDescription(item.snippet));
      var tagItems = itemTags(item, L, defaultLang);
      var tagsHtml = '';
      for (var t = 0; t < tagItems.length; t++) {
        tagsHtml += '<span class="bg-[#90efef] text-[#006e6e] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider whitespace-nowrap">' +
          escapeHtml(tagItems[t]) + '</span>';
      }
      var tagScrollerId = 'tagScrollerGI' + idx;
      var imageHtml = imageOrPlaceholder(
        item,
        'w-full h-56 object-cover rounded-lg',
        'bg-gradient-to-br from-[#dae1ff] to-[#b3c5ff]'
      );
      var sum = dualText(item.summary_vi || '', item.summary_en || '', bilingual, defaultLang);
      var cur = dualText(L.summary_ai_curator.vi, L.summary_ai_curator.en, bilingual, defaultLang);
      var tagsJson = tagsJsonAttr(item);
      cards +=
        '<article class="bg-white rounded-lg p-6 group transition-all hover:bg-[#edeeef] report-article-filterable" data-item-tags="' +
        tagsJson +
        '">' +
          '<div class="flex flex-col gap-4">' +
            '<div>' + imageHtml + '</div>' +
            '<div>' +
              '<h2 class="text-2xl font-bold text-[#0052d1] group-hover:text-[#156aff] transition-colors">' + titleHtml(item, idx) + '</h2>' +
              '<div class="mt-2 flex items-center gap-2">' +
                '<div id="' + tagScrollerId + '" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1">' + tagsHtml + '</div>' +
                '<button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="' + tagScrollerId + '">&gt;</button>' +
              '</div>' +
            '</div>' +
            '<div class="flex items-center gap-4 text-[#414755] text-sm font-semibold">' +
              '<span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">calendar_today</span>' + published + '</span>' +
            '</div>' +
            '<p class="text-[#414755] leading-relaxed">' + snippet + '</p>' +
            '<div class="mt-2 p-5 bg-[#93f2f2]/20 border-l-4 border-[#006a6a] rounded-r-lg">' +
              '<div class="flex items-center gap-2 mb-2 text-[#006a6a] font-bold text-xs uppercase tracking-widest">' +
                '<span class="material-symbols-outlined text-lg" style="font-variation-settings: \'FILL\' 1;">auto_awesome</span>' + cur +
              '</div>' +
              '<p class="text-[#004f4f] text-sm font-medium italic">' + sum + '</p>' +
            '</div>' +
          '</div>' +
        '</article>';
    }
    return cards;
  }

  function renderNewFeatures(data, L, bilingual, defaultLang, panelId) {
    panelId = panelId || '';
    if (!data || !data.length) return renderEmpty(L, bilingual, defaultLang);
    var cards = '';
    for (var i = 0; i < data.length; i++) {
      var item = data[i];
      var idx = i + 1;
      var published = formatPublished(item.published);
      var snippet = escapeHtml(cleanDescription(item.snippet));
      var featureBadge = dualText(L.feature_badge.vi, L.feature_badge.en, bilingual, defaultLang);
      var tagItems = itemTags(item, L, defaultLang);
      var tagsHtml = '';
      for (var t = 0; t < tagItems.length; t++) {
        tagsHtml +=
          '<span class="bg-[#90efef] text-[#006e6e] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider whitespace-nowrap">' +
          escapeHtml(tagItems[t]) +
          '</span>';
      }
      var tagScrollerId = 'tagScrollerNF' + panelId + idx;
      var tagsJson = tagsJsonAttr(item);
      var mediaHtml = imageOrPlaceholder(
        item,
        'w-full h-full object-cover rounded-lg',
        'bg-gradient-to-br from-[#c1c6d7] to-[#e1e3e4]'
      );
      var sum = dualText(item.summary_vi || '', item.summary_en || '', bilingual, defaultLang);
      var cur = dualText(L.summary_curator.vi, L.summary_curator.en, bilingual, defaultLang);
      cards +=
        '<article class="flex flex-col md:flex-row gap-8 bg-white p-6 rounded-lg transition-all hover:bg-[#edeeef] report-article-filterable" data-item-tags="' +
        tagsJson +
        '">' +
          '<div class="w-full md:w-1/3 aspect-video overflow-hidden rounded-lg">' + mediaHtml + '</div>' +
          '<div class="flex-1 flex flex-col justify-center">' +
            '<div class="flex items-center gap-3 mb-3">' +
              '<span class="text-[10px] font-black text-[#006a6a] tracking-widest uppercase">' + featureBadge + '</span>' +
              '<span class="text-[10px] font-medium text-[#414755]/70 uppercase">' + published + '</span>' +
            '</div>' +
            '<h4 class="text-2xl font-extrabold text-[#191c1d] mb-3 tracking-tight">' + titleHtml(item, idx) + '</h4>' +
            '<div class="mb-3 flex items-center gap-2">' +
            '<div id="' +
            tagScrollerId +
            '" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1 flex-wrap">' +
            tagsHtml +
            '</div>' +
            '<button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="' +
            tagScrollerId +
            '">&gt;</button>' +
            '</div>' +
            '<p class="text-[#414755] text-base mb-6 leading-relaxed">' + snippet + '</p>' +
            '<div class="bg-[#93f2f2]/20 p-4 rounded-lg border-l-4 border-[#006a6a]">' +
              '<div class="flex items-center gap-2 mb-1">' +
                '<span class="material-symbols-outlined text-[#006a6a] text-sm" style="font-variation-settings: \'FILL\' 1;">auto_awesome</span>' +
                '<span class="text-[10px] font-black text-[#006a6a] uppercase tracking-tight">' + cur + '</span>' +
              '</div>' +
              '<p class="text-xs text-[#004f4f] leading-normal">' + sum + '</p>' +
            '</div>' +
          '</div>' +
        '</article>';
    }
    return cards;
  }

  function renderNewFeaturesGrouped(modulesNF, overviewsNF, L, bilingual, defaultLang) {
    var subs = [
      { key: 'samsung', labelKey: 'new_features_samsung', panelId: 'nfSamsung' },
      { key: 'iphone', labelKey: 'new_features_iphone', panelId: 'nfIphone' },
      { key: 'china', labelKey: 'new_features_china', panelId: 'nfChina' },
    ];
    var pills = '';
    var panels = '';
    for (var s = 0; s < subs.length; s++) {
      var sk = subs[s].key;
      var lk = subs[s].labelKey;
      var panelId = subs[s].panelId;
      var isFirst = s === 0;
      var data = modulesNF && modulesNF[sk] ? modulesNF[sk] : [];
      var ov =
        overviewsNF && overviewsNF[sk] ? overviewsNF[sk] : { vi: '', en: '' };
      var Lt = L[lk] || { vi: sk, en: sk };
      var label = dualText(Lt.vi, Lt.en, bilingual, defaultLang);
      var cards = renderNewFeatures(data, L, bilingual, defaultLang, panelId);
      var filterShell = renderTagFilterShell(L, bilingual, defaultLang, 'report-tag-filter-' + panelId);
      var ovBlock = renderOverviewBlock(ov, L, bilingual, defaultLang);
      var ovSection = ovBlock ? '<div class="mb-8">' + ovBlock + '</div>' : '';
      var pillCls = isFirst ? 'nf-pill nf-pill-active' : 'nf-pill nf-pill-idle';
      var ariaSel = isFirst ? 'true' : 'false';
      pills +=
        '<button type="button" class="' +
        pillCls +
        ' px-5 py-2 rounded-full text-sm font-semibold transition-all" data-nf-target="' +
        panelId +
        '" role="tab" aria-selected="' +
        ariaSel +
        '">' +
        label +
        '</button>';
      var openCls = isFirst ? ' new-features-subpanel-open' : '';
      var ariaHidden = isFirst ? 'false' : 'true';
      panels +=
        '<div id="' +
        panelId +
        '" class="new-features-subpanel space-y-6' +
        openCls +
        '" role="tabpanel" aria-hidden="' +
        ariaHidden +
        '">' +
        ovSection +
        '<div class="report-tag-scope space-y-6">' +
        filterShell +
        '<div class="space-y-8">' +
        cards +
        '</div></div></div>';
    }
    return (
      '<div class="flex flex-wrap gap-3 mb-8" id="new-features-subnav" role="tablist">' +
      pills +
      '</div>' +
      '<div id="report-new-features-panels" class="relative">' +
      panels +
      '</div>'
    );
  }

  function renderHotLike(data, L, bilingual, defaultLang, badgeKey, tagScrollerPrefix) {
    tagScrollerPrefix = tagScrollerPrefix || 'hl';
    if (!data || !data.length) return renderEmpty(L, bilingual, defaultLang);
    var B = L[badgeKey];
    var badgeDual = dualText(B.vi, B.en, bilingual, defaultLang);
    var cards = '';
    for (var i = 0; i < data.length; i++) {
      var item = data[i];
      var idx = i + 1;
      var published = formatPublished(item.published);
      var snippet = escapeHtml(cleanDescription(item.snippet));
      var tagItems = itemTags(item, L, defaultLang);
      var tagsHtml = '';
      for (var t = 0; t < tagItems.length; t++) {
        tagsHtml +=
          '<span class="bg-[#90efef] text-[#006e6e] px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider whitespace-nowrap">' +
          escapeHtml(tagItems[t]) +
          '</span>';
      }
      var tagScrollerId = 'tagScroller' + tagScrollerPrefix + idx;
      var tagsJson = tagsJsonAttr(item);
      var mediaHtml = imageOrPlaceholder(
        item,
        'w-full h-48 object-cover rounded-lg',
        'bg-gradient-to-br from-[#dae1ff] to-[#b3c5ff]'
      );
      var sum = dualText(item.summary_vi || '', item.summary_en || '', bilingual, defaultLang);
      var intel = dualText(L.summary_ai_intel.vi, L.summary_ai_intel.en, bilingual, defaultLang);
      cards +=
        '<article class="group bg-white rounded-lg p-6 lg:p-8 flex flex-col lg:flex-row gap-8 transition-transform hover:scale-[1.01] duration-300 report-article-filterable" data-item-tags="' +
        tagsJson +
        '">' +
          '<div class="lg:w-1/3 shrink-0">' + mediaHtml + '</div>' +
          '<div class="flex-1 flex flex-col">' +
            '<div class="flex items-center gap-3 mb-3">' +
              '<span class="bg-[#ffdad6] text-[#93000a] text-[10px] px-2 py-1 font-black uppercase tracking-tighter rounded-sm">' + badgeDual + '</span>' +
              '<span class="text-[#414755] text-xs font-medium uppercase tracking-widest">' + published + '</span>' +
            '</div>' +
            '<h2 class="font-headline font-bold text-2xl text-[#191c1d] mb-3 group-hover:text-[#0052d1] transition-colors">' + titleHtml(item, idx) + '</h2>' +
            '<div class="mb-4 flex items-center gap-2">' +
            '<div id="' +
            tagScrollerId +
            '" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1 flex-wrap">' +
            tagsHtml +
            '</div>' +
            '<button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="' +
            tagScrollerId +
            '">&gt;</button>' +
            '</div>' +
            '<p class="text-[#414755] leading-relaxed mb-6">' + snippet + '</p>' +
            '<div class="bg-[#93f2f2]/20 p-4 rounded-lg border-l-4 border-[#006a6a] flex items-start gap-4">' +
              '<span class="material-symbols-outlined text-[#006a6a] text-xl">auto_awesome</span>' +
              '<div>' +
                '<p class="text-xs font-bold text-[#006a6a] uppercase tracking-widest mb-1">' + intel + '</p>' +
                '<p class="text-sm text-[#191c1d] leading-tight font-medium">' + sum + '</p>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</article>';
    }
    return cards;
  }

  function siUpdateTagNextVisibility() {
    document.querySelectorAll('.tag-next').forEach(function (button) {
      var targetId = button.getAttribute('data-target');
      var scroller = document.getElementById(targetId);
      if (!scroller) return;
      var hasOverflow = scroller.scrollWidth > scroller.clientWidth + 2;
      button.classList.toggle('hidden', !hasOverflow);
    });
  }

  function renderAll(data) {
    var L = data.labels;
    var bi = data.bilingual;
    var dl = data.defaultLang;
    var m = data.modules;
    var o = data.overviews;

    var elG = document.getElementById('report-list-globalInformation');
    var elNfRoot = document.getElementById('report-new-features-root');
    var elH = document.getElementById('report-list-hotAndroidIssues');
    var elP = document.getElementById('report-list-patentTrend');
    if (elG) elG.innerHTML = renderGlobalInformation(m.globalInformation, L, bi, dl);
    if (elNfRoot) {
      elNfRoot.innerHTML = renderNewFeaturesGrouped(m.newFeatures || {}, o.newFeatures || {}, L, bi, dl);
    }
    if (elH) elH.innerHTML = renderHotLike(m.hotAndroidIssues, L, bi, dl, 'issue_badge', 'Hot');
    if (elP) elP.innerHTML = renderHotLike(m.patentTrend, L, bi, dl, 'patent_badge', 'Patent');

    var og = document.getElementById('report-overview-globalInformation');
    var oh = document.getElementById('report-overview-hotAndroidIssues');
    var op = document.getElementById('report-overview-patentTrend');
    if (og) og.innerHTML = renderOverviewBlock(o.globalInformation, L, bi, dl);
    if (oh) oh.innerHTML = renderOverviewBlock(o.hotAndroidIssues, L, bi, dl);
    if (op) op.innerHTML = renderOverviewBlock(o.patentTrend, L, bi, dl);

    siUpdateTagNextVisibility();
    if (typeof window.__SI_initReportTagFilters === 'function') {
      window.__SI_initReportTagFilters(document);
    }
    if (bi && typeof window.__SI_switchLanguage === 'function') {
      window.__SI_switchLanguage(dl);
    }
  }

  function mergeOverviewFlat(target, savedOv) {
    if (!target || typeof target !== 'object') target = { vi: '', en: '' };
    if (!savedOv || typeof savedOv !== 'object') return target;
    return {
      vi: savedOv.vi != null ? savedOv.vi : target.vi,
      en: savedOv.en != null ? savedOv.en : target.en,
    };
  }

  function ensureNewFeaturesShape(data) {
    if (!data.modules) data.modules = {};
    var nf = data.modules.newFeatures;
    if (!nf || Array.isArray(nf)) {
      var arr = Array.isArray(nf) ? nf.slice() : [];
      data.modules.newFeatures = {
        samsung: arr.length ? arr : [],
        iphone: [],
        china: [],
      };
    } else {
      if (!Array.isArray(nf.samsung)) data.modules.newFeatures.samsung = [];
      if (!Array.isArray(nf.iphone)) data.modules.newFeatures.iphone = [];
      if (!Array.isArray(nf.china)) data.modules.newFeatures.china = [];
    }
    if (!data.overviews) data.overviews = {};
    var ovnf = data.overviews.newFeatures;
    if (!ovnf || ovnf.vi !== undefined || ovnf.en !== undefined) {
      var old = ovnf && (ovnf.vi !== undefined || ovnf.en !== undefined) ? ovnf : { vi: '', en: '' };
      data.overviews.newFeatures = {
        samsung: { vi: old.vi || '', en: old.en || '' },
        iphone: { vi: '', en: '' },
        china: { vi: '', en: '' },
      };
    } else {
      ['samsung', 'iphone', 'china'].forEach(function (sub) {
        if (!data.overviews.newFeatures[sub] || typeof data.overviews.newFeatures[sub] !== 'object') {
          data.overviews.newFeatures[sub] = { vi: '', en: '' };
        }
      });
    }
  }

  function loadStorageMerge(data) {
    ensureNewFeaturesShape(data);
    var key = STORAGE_PREFIX + data.reportId;
    var raw = null;
    try {
      raw = localStorage.getItem(key);
    } catch (e) {
      return data;
    }
    if (!raw) return data;
    try {
      var saved = JSON.parse(raw);
      if (saved.modules) {
        MODULE_KEYS.forEach(function (k) {
          if (k === 'newFeatures') {
            var snf = saved.modules.newFeatures;
            if (snf && typeof snf === 'object' && !Array.isArray(snf)) {
              if (Array.isArray(snf.samsung)) data.modules.newFeatures.samsung = snf.samsung;
              if (Array.isArray(snf.iphone)) data.modules.newFeatures.iphone = snf.iphone;
              if (Array.isArray(snf.china)) data.modules.newFeatures.china = snf.china;
            } else if (Array.isArray(snf)) {
              data.modules.newFeatures.samsung = snf;
            }
          } else if (Array.isArray(saved.modules[k])) {
            data.modules[k] = saved.modules[k];
          }
        });
      }
      if (saved.overviews) {
        MODULE_KEYS.forEach(function (k) {
          if (k === 'newFeatures') {
            var so = saved.overviews.newFeatures;
            if (so && typeof so === 'object') {
              if (so.samsung || so.iphone || so.china) {
                ['samsung', 'iphone', 'china'].forEach(function (sub) {
                  if (so[sub] && typeof so[sub] === 'object') {
                    data.overviews.newFeatures[sub] = mergeOverviewFlat(
                      data.overviews.newFeatures[sub],
                      so[sub]
                    );
                  }
                });
              } else if (so.vi !== undefined || so.en !== undefined) {
                data.overviews.newFeatures.samsung = mergeOverviewFlat(
                  data.overviews.newFeatures.samsung,
                  so
                );
              }
            }
          } else if (saved.overviews[k] && typeof saved.overviews[k] === 'object') {
            data.overviews[k] = mergeOverviewFlat(data.overviews[k], saved.overviews[k]);
          }
        });
      }
    } catch (e2) {}
    return data;
  }

  function saveToStorage(data) {
    var key = STORAGE_PREFIX + data.reportId;
    var payload = {
      modules: data.modules,
      overviews: data.overviews,
      savedAt: new Date().toISOString(),
    };
    try {
      localStorage.setItem(key, JSON.stringify(payload));
    } catch (e) {
      alert('Could not save to localStorage: ' + (e.message || e));
      return false;
    }
    return true;
  }

  function emptyArticle() {
    return {
      title: '',
      link: '',
      published: '',
      snippet: '',
      image: '',
      tags: [],
      summary_vi: '',
      summary_en: '',
      content: '',
    };
  }

  function parseTags(str) {
    if (!str || !String(str).trim()) return [];
    return String(str)
      .split(',')
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
  }

  function buildAdminPanel(host, data) {
    var currentTab = 'globalInformation';

    var shell = document.createElement('div');
    shell.style.cssText =
      'position:fixed;bottom:16px;right:16px;z-index:100000;font-size:14px;line-height:1.4;max-width:100%;';

    var fab = document.createElement('button');
    fab.type = 'button';
    fab.textContent = 'Quản lý nội dung';
    fab.style.cssText =
      'background:#0052d1;color:#fff;border:none;border-radius:999px;padding:12px 18px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(0,82,209,.35);font-family:inherit;';
    fab.title = 'Chỉnh sửa bài báo (đã xác thực)';

    var panel = document.createElement('div');
    panel.style.cssText =
      'display:none;position:absolute;bottom:56px;right:0;width:min(440px,calc(100vw - 32px));max-height:min(78vh,720px);overflow:auto;background:#fff;border:1px solid #e1e3e4;border-radius:12px;box-shadow:0 12px 40px rgba(25,28,29,.15);padding:16px;text-align:left;color:#191c1d;';

    var tabRow = document.createElement('div');
    tabRow.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;';
    var tabLabels = {
      globalInformation: 'Toàn cầu',
      newFeatures: 'Tính năng mới',
      hotAndroidIssues: 'Hot Android',
      patentTrend: 'Patent',
    };

    var contentArea = document.createElement('div');

    function updateTabStyles() {
      Array.prototype.forEach.call(tabRow.querySelectorAll('button'), function (b, i) {
        var key = MODULE_KEYS[i];
        var on = key === currentTab;
        b.style.background = on ? '#0052d1' : '#fff';
        b.style.color = on ? '#fff' : '#191c1d';
        b.style.borderColor = on ? '#0052d1' : '#c1c6d7';
      });
    }

    function flushOverviewEditorsToData() {
      var ed = shell._getOverviewEditors && shell._getOverviewEditors();
      if (!ed) return;
      if (ed.type === 'newFeaturesMulti') {
        ['samsung', 'iphone', 'china'].forEach(function (sub) {
          var vi = document.getElementById('si-nf-ov-' + sub + '-vi');
          var en = document.getElementById('si-nf-ov-' + sub + '-en');
          if (vi && en && data.overviews.newFeatures) {
            data.overviews.newFeatures[sub] = { vi: vi.value, en: en.value };
          }
        });
        return;
      }
      if (ed.vi && ed.en && ed.moduleKey) {
        data.overviews[ed.moduleKey] = { vi: ed.vi.value, en: ed.en.value };
      }
    }

    function renderTabContent() {
      contentArea.innerHTML = '';
      var mk = currentTab;

      if (mk === 'newFeatures') {
        if (!data.modules.newFeatures || typeof data.modules.newFeatures !== 'object') {
          data.modules.newFeatures = { samsung: [], iphone: [], china: [] };
        }
        if (!data.overviews.newFeatures || typeof data.overviews.newFeatures !== 'object') {
          data.overviews.newFeatures = {
            samsung: { vi: '', en: '' },
            iphone: { vi: '', en: '' },
            china: { vi: '', en: '' },
          };
        }
        var nfSubs = [
          { key: 'samsung', label: 'Samsung' },
          { key: 'iphone', label: 'iPhone' },
          { key: 'china', label: 'Trung Quốc / China' },
        ];
        nfSubs.forEach(function (ns) {
          var sub = ns.key;
          if (!Array.isArray(data.modules.newFeatures[sub])) data.modules.newFeatures[sub] = [];
          if (!data.overviews.newFeatures[sub]) data.overviews.newFeatures[sub] = { vi: '', en: '' };

          var sec = document.createElement('div');
          sec.style.cssText =
            'margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid #edeeef;';
          var h = document.createElement('div');
          h.textContent = ns.label;
          h.style.cssText = 'font-weight:800;margin-bottom:10px;color:#0052d1;font-size:14px;';
          sec.appendChild(h);

          var ovLab = document.createElement('div');
          ovLab.textContent = 'Tổng quan / Overall (' + ns.label + ')';
          ovLab.style.cssText =
            'font-weight:700;margin-bottom:6px;color:#414755;font-size:11px;text-transform:uppercase;';
          sec.appendChild(ovLab);

          var l1 = document.createElement('label');
          l1.textContent = 'Tiếng Việt';
          l1.style.cssText = 'display:block;font-size:11px;color:#414755;margin-bottom:2px;';
          var taVi = document.createElement('textarea');
          taVi.id = 'si-nf-ov-' + sub + '-vi';
          taVi.rows = 2;
          taVi.style.cssText =
            'width:100%;padding:6px;border:1px solid #c1c6d7;border-radius:8px;margin-bottom:8px;font-family:inherit;resize:vertical;font-size:13px;';
          taVi.value = data.overviews.newFeatures[sub].vi || '';
          sec.appendChild(l1);
          sec.appendChild(taVi);

          var l2 = document.createElement('label');
          l2.textContent = 'English';
          l2.style.cssText = 'display:block;font-size:11px;color:#414755;margin-bottom:2px;';
          var taEn = document.createElement('textarea');
          taEn.id = 'si-nf-ov-' + sub + '-en';
          taEn.rows = 2;
          taEn.style.cssText =
            'width:100%;padding:6px;border:1px solid #c1c6d7;border-radius:8px;margin-bottom:10px;font-family:inherit;resize:vertical;font-size:13px;';
          taEn.value = data.overviews.newFeatures[sub].en || '';
          sec.appendChild(l2);
          sec.appendChild(taEn);

          var artTitle = document.createElement('div');
          artTitle.textContent = 'Bài viết / Articles';
          artTitle.style.cssText = 'font-weight:700;margin:6px 0;color:#191c1d;font-size:12px;';
          sec.appendChild(artTitle);

          var articles = data.modules.newFeatures[sub];
          articles.forEach(function (article, index) {
            var box = document.createElement('div');
            box.style.cssText =
              'border:1px solid #edeeef;border-radius:10px;padding:10px;margin-bottom:10px;background:#fafbfc;';

            var hdr = document.createElement('div');
            hdr.style.cssText =
              'font-weight:600;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;gap:8px;';
            hdr.innerHTML = '<span>#' + (index + 1) + '</span>';
            var del = document.createElement('button');
            del.type = 'button';
            del.textContent = 'Xóa';
            del.style.cssText =
              'background:#ffdad6;color:#93000a;border:none;border-radius:6px;padding:4px 10px;font-size:12px;cursor:pointer;font-family:inherit;';
            del.addEventListener(
              'click',
              function (subKey, idx) {
                return function () {
                  if (!confirm('Xóa bài này? / Delete this article?')) return;
                  data.modules.newFeatures[subKey].splice(idx, 1);
                  renderTabContent();
                };
              }(sub, index)
            );
            hdr.appendChild(del);
            box.appendChild(hdr);

            function addField(label, key, multiline) {
              var lb = document.createElement('label');
              lb.textContent = label;
              lb.style.cssText = 'display:block;font-size:11px;color:#414755;margin:6px 0 2px;';
              var inp = multiline ? document.createElement('textarea') : document.createElement('input');
              if (!multiline) {
                inp.type = 'text';
                inp.style.cssText =
                  'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;';
              } else {
                inp.rows = key === 'snippet' ? 3 : 2;
                inp.style.cssText =
                  'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;resize:vertical;';
              }
              inp.value = article[key] != null ? String(article[key]) : '';
              inp.dataset.articleIndex = String(index);
              inp.dataset.articleKey = key;
              inp.addEventListener(
                'input',
                function (subKey) {
                  return function () {
                    var ai = parseInt(inp.dataset.articleIndex, 10);
                    var k = inp.dataset.articleKey;
                    if (!data.modules.newFeatures[subKey][ai]) return;
                    data.modules.newFeatures[subKey][ai][k] = inp.value;
                  };
                }(sub)
              );
              box.appendChild(lb);
              box.appendChild(inp);
            }

            addField('Tiêu đề / Title', 'title', false);
            addField('Link', 'link', false);
            addField('Ngày (ISO) / Published', 'published', false);
            addField('Ảnh URL / Image', 'image', false);

            var lbTags = document.createElement('label');
            lbTags.textContent = 'Tags (phân cách bằng dấu phẩy) / Tags';
            lbTags.style.cssText = 'display:block;font-size:11px;color:#414755;margin:6px 0 2px;';
            var tagsInput = document.createElement('input');
            tagsInput.type = 'text';
            tagsInput.style.cssText =
              'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;';
            tagsInput.value = Array.isArray(article.tags) ? article.tags.join(', ') : '';
            tagsInput.addEventListener(
              'input',
              function (subKey, idx) {
                return function () {
                  if (!data.modules.newFeatures[subKey][idx]) return;
                  data.modules.newFeatures[subKey][idx].tags = parseTags(tagsInput.value);
                };
              }(sub, index)
            );
            box.appendChild(lbTags);
            box.appendChild(tagsInput);

            addField('Mô tả (snippet) / Snippet', 'snippet', true);
            addField('Tóm tắt AI (VI)', 'summary_vi', true);
            addField('Tóm tắt AI (EN)', 'summary_en', true);

            sec.appendChild(box);
          });

          var addBtn = document.createElement('button');
          addBtn.type = 'button';
          addBtn.textContent = '+ Thêm bài (' + ns.label + ')';
          addBtn.style.cssText =
            'width:100%;margin-top:6px;margin-bottom:8px;padding:8px;background:#edeeef;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-family:inherit;color:#191c1d;font-size:12px;';
          addBtn.addEventListener(
            'click',
            function (subKey) {
              return function () {
                data.modules.newFeatures[subKey].push(emptyArticle());
                renderTabContent();
              };
            }(sub)
          );
          sec.appendChild(addBtn);
          contentArea.appendChild(sec);
        });

        shell._getOverviewEditors = function () {
          return { type: 'newFeaturesMulti', moduleKey: 'newFeatures' };
        };
        return;
      }

      if (!data.modules[mk]) data.modules[mk] = [];
      if (!data.overviews[mk]) data.overviews[mk] = { vi: '', en: '' };
      var ov = data.overviews[mk];
      var articles = data.modules[mk];

      var ovTitle = document.createElement('div');
      ovTitle.textContent = 'Overall / Tổng quan';
      ovTitle.style.cssText = 'font-weight:700;margin-bottom:8px;color:#0052d1;font-size:12px;text-transform:uppercase;';
      contentArea.appendChild(ovTitle);

      var l1 = document.createElement('label');
      l1.textContent = 'Tiếng Việt';
      l1.style.cssText = 'display:block;font-size:12px;color:#414755;margin-bottom:4px;';
      var taVi = document.createElement('textarea');
      taVi.rows = 3;
      taVi.style.cssText = 'width:100%;padding:8px;border:1px solid #c1c6d7;border-radius:8px;margin-bottom:10px;font-family:inherit;resize:vertical;';
      taVi.value = ov.vi || '';
      taVi.dataset.field = 'ov-vi';
      contentArea.appendChild(l1);
      contentArea.appendChild(taVi);

      var l2 = document.createElement('label');
      l2.textContent = 'English';
      l2.style.cssText = 'display:block;font-size:12px;color:#414755;margin-bottom:4px;';
      var taEn = document.createElement('textarea');
      taEn.rows = 3;
      taEn.style.cssText = 'width:100%;padding:8px;border:1px solid #c1c6d7;border-radius:8px;margin-bottom:14px;font-family:inherit;resize:vertical;';
      taEn.value = ov.en || '';
      taEn.dataset.field = 'ov-en';
      contentArea.appendChild(l2);
      contentArea.appendChild(taEn);

      var artTitle = document.createElement('div');
      artTitle.textContent = 'Bài viết / Articles';
      artTitle.style.cssText = 'font-weight:700;margin:8px 0;color:#191c1d;';
      contentArea.appendChild(artTitle);

      articles.forEach(function (article, index) {
        var box = document.createElement('div');
        box.style.cssText = 'border:1px solid #edeeef;border-radius:10px;padding:10px;margin-bottom:10px;background:#fafbfc;';

        var hdr = document.createElement('div');
        hdr.style.cssText = 'font-weight:600;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;gap:8px;';
        hdr.innerHTML = '<span>#' + (index + 1) + '</span>';
        var del = document.createElement('button');
        del.type = 'button';
        del.textContent = 'Xóa';
        del.style.cssText = 'background:#ffdad6;color:#93000a;border:none;border-radius:6px;padding:4px 10px;font-size:12px;cursor:pointer;font-family:inherit;';
        del.addEventListener('click', function () {
          if (!confirm('Xóa bài này? / Delete this article?')) return;
          data.modules[mk].splice(index, 1);
          renderTabContent();
        });
        hdr.appendChild(del);
        box.appendChild(hdr);

        function addField(label, key, multiline) {
          var lb = document.createElement('label');
          lb.textContent = label;
          lb.style.cssText = 'display:block;font-size:11px;color:#414755;margin:6px 0 2px;';
          var inp = multiline ? document.createElement('textarea') : document.createElement('input');
          if (!multiline) {
            inp.type = 'text';
            inp.style.cssText = 'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;';
          } else {
            inp.rows = key === 'snippet' ? 3 : 2;
            inp.style.cssText = 'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;resize:vertical;';
          }
          inp.value = article[key] != null ? String(article[key]) : '';
          inp.dataset.articleIndex = String(index);
          inp.dataset.articleKey = key;
          inp.addEventListener('input', function () {
            var ai = parseInt(inp.dataset.articleIndex, 10);
            var k = inp.dataset.articleKey;
            if (!data.modules[mk][ai]) return;
            data.modules[mk][ai][k] = inp.value;
          });
          box.appendChild(lb);
          box.appendChild(inp);
        }

        addField('Tiêu đề / Title', 'title', false);
        addField('Link', 'link', false);
        addField('Ngày (ISO) / Published', 'published', false);
        addField('Ảnh URL / Image', 'image', false);

        var lbTags = document.createElement('label');
        lbTags.textContent = 'Tags (phân cách bằng dấu phẩy) / Tags (comma-separated)';
        lbTags.style.cssText = 'display:block;font-size:11px;color:#414755;margin:6px 0 2px;';
        var tagsInput = document.createElement('input');
        tagsInput.type = 'text';
        tagsInput.style.cssText = 'width:100%;padding:6px 8px;border:1px solid #c1c6d7;border-radius:6px;font-family:inherit;font-size:13px;';
        tagsInput.value = Array.isArray(article.tags) ? article.tags.join(', ') : '';
        tagsInput.dataset.articleIndex = String(index);
        tagsInput.addEventListener('input', function () {
          var ai = parseInt(tagsInput.dataset.articleIndex, 10);
          if (!data.modules[mk][ai]) return;
          data.modules[mk][ai].tags = parseTags(tagsInput.value);
        });
        box.appendChild(lbTags);
        box.appendChild(tagsInput);

        addField('Mô tả (snippet HTML hoặc text) / Snippet', 'snippet', true);
        addField('Tóm tắt AI (VI) / Summary VI', 'summary_vi', true);
        addField('Tóm tắt AI (EN) / Summary EN', 'summary_en', true);

        contentArea.appendChild(box);
      });

      var addBtn = document.createElement('button');
      addBtn.type = 'button';
      addBtn.textContent = '+ Thêm bài / Add article';
      addBtn.style.cssText =
        'width:100%;margin-top:8px;padding:10px;background:#edeeef;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-family:inherit;color:#191c1d;';
      addBtn.addEventListener('click', function () {
        data.modules[mk].push(emptyArticle());
        renderTabContent();
      });
      contentArea.appendChild(addBtn);

      shell._getOverviewEditors = function () {
        return { vi: taVi, en: taEn, moduleKey: mk };
      };
    }

    MODULE_KEYS.forEach(function (mk) {
      var tb = document.createElement('button');
      tb.type = 'button';
      tb.textContent = tabLabels[mk];
      tb.style.cssText =
        'padding:6px 10px;border-radius:999px;border:1px solid #c1c6d7;cursor:pointer;font-size:12px;font-family:inherit;';
      tb.addEventListener('click', function () {
        flushOverviewEditorsToData();
        currentTab = mk;
        updateTabStyles();
        renderTabContent();
      });
      tabRow.appendChild(tb);
    });
    updateTabStyles();

    var btnRow = document.createElement('div');
    btnRow.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;';

    var saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.textContent = 'Lưu / Save';
    saveBtn.style.cssText =
      'flex:1;min-width:120px;padding:10px 14px;background:#006a6a;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-family:inherit;';

    var downloadBtn = document.createElement('button');
    downloadBtn.type = 'button';
    downloadBtn.textContent = 'Tải JSON';
    downloadBtn.style.cssText =
      'flex:1;min-width:100px;padding:10px 14px;background:#fff;color:#0052d1;border:1px solid #0052d1;border-radius:8px;font-weight:600;cursor:pointer;font-family:inherit;';

    var closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.textContent = 'Đóng panel';
    closeBtn.title = 'Chỉ ẩn bảng điều khiển, giữ nút Quản lý / Collapse panel only';
    closeBtn.style.cssText =
      'padding:10px 14px;background:transparent;color:#414755;border:1px solid #c1c6d7;border-radius:8px;cursor:pointer;font-family:inherit;';

    var exitRow = document.createElement('div');
    exitRow.style.cssText = 'margin-top:12px;padding-top:12px;border-top:1px solid #edeeef;';
    var exitAdminBtn = document.createElement('button');
    exitAdminBtn.type = 'button';
    exitAdminBtn.textContent = 'Thoát chế độ quản trị (giữ nội dung đã chỉnh)';
    exitAdminBtn.title =
      'Lưu toàn bộ lên trình duyệt, cập nhật trang và ẩn chế độ quản trị. Mở lại: click 3 lần Security Insights + mật khẩu. / Save all, update page, exit admin. Reopen: triple-click brand + password.';
    exitAdminBtn.style.cssText =
      'width:100%;padding:11px 14px;background:#f8f9fa;color:#191c1d;border:1px solid #c1c6d7;border-radius:8px;cursor:pointer;font-family:inherit;font-weight:600;font-size:13px;';

    function flushCurrentOverview() {
      flushOverviewEditorsToData();
    }

    exitAdminBtn.addEventListener('click', function () {
      flushCurrentOverview();
      saveToStorage(data);
      renderAll(data);
      try {
        if (shell.parentNode) shell.parentNode.removeChild(shell);
      } catch (e1) {}
      host.dataset.mounted = '';
    });

    saveBtn.addEventListener('click', function () {
      flushCurrentOverview();
      if (saveToStorage(data)) {
        renderAll(data);
        alert('Đã lưu. / Saved.');
      }
    });

    downloadBtn.addEventListener('click', function () {
      flushCurrentOverview();
      var blob = new Blob([JSON.stringify({ modules: data.modules, overviews: data.overviews }, null, 2)], {
        type: 'application/json',
      });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'security-report-edit-' + data.reportId + '.json';
      a.click();
      URL.revokeObjectURL(a.href);
    });

    closeBtn.addEventListener('click', function () {
      panel.style.display = 'none';
    });

    fab.addEventListener('click', function () {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
      if (panel.style.display === 'block') renderTabContent();
    });

    btnRow.appendChild(saveBtn);
    btnRow.appendChild(downloadBtn);
    btnRow.appendChild(closeBtn);

    panel.appendChild(tabRow);
    panel.appendChild(contentArea);
    panel.appendChild(btnRow);
    exitRow.appendChild(exitAdminBtn);
    panel.appendChild(exitRow);

    shell.appendChild(fab);
    shell.appendChild(panel);
    host.appendChild(shell);

    renderTabContent();
  }

  function showPasswordModal(onSuccess) {
    var ov = document.createElement('div');
    ov.style.cssText =
      'position:fixed;inset:0;background:rgba(25,28,29,.5);z-index:100001;display:flex;align-items:center;justify-content:center;padding:16px;';
    var box = document.createElement('div');
    box.style.cssText = 'background:#fff;border-radius:12px;padding:20px;max-width:360px;width:100%;box-shadow:0 16px 48px rgba(0,0,0,.2);font-family:inherit;';
    box.innerHTML =
      '<p style="margin:0 0 12px;font-weight:700;color:#191c1d;">Nhập mật khẩu quản trị / Admin password</p>';
    var input = document.createElement('input');
    input.type = 'password';
    input.style.cssText = 'width:100%;padding:10px 12px;border:1px solid #c1c6d7;border-radius:8px;font-size:15px;margin-bottom:12px;';
    input.autocomplete = 'off';
    var row = document.createElement('div');
    row.style.cssText = 'display:flex;gap:8px;justify-content:flex-end;';
    var ok = document.createElement('button');
    ok.type = 'button';
    ok.textContent = 'OK';
    ok.style.cssText = 'padding:8px 16px;background:#0052d1;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;';
    var cancel = document.createElement('button');
    cancel.type = 'button';
    cancel.textContent = 'Hủy';
    cancel.style.cssText = 'padding:8px 16px;background:#edeeef;border:none;border-radius:8px;cursor:pointer;';
    function cleanup() {
      try {
        document.body.removeChild(ov);
      } catch (e) {}
    }
    ok.addEventListener('click', function () {
      if (input.value === ADMIN_PASSWORD) {
        cleanup();
        onSuccess();
      } else {
        alert('Sai mật khẩu. / Wrong password.');
        input.value = '';
        input.focus();
      }
    });
    cancel.addEventListener('click', cleanup);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') ok.click();
    });
    row.appendChild(cancel);
    row.appendChild(ok);
    box.appendChild(input);
    box.appendChild(row);
    ov.appendChild(box);
    document.body.appendChild(ov);
    input.focus();
  }

  function setupBrandUnlock(data) {
    var brand = document.getElementById('report-brand-unlock');
    if (!brand) return;
    var clicks = 0;
    var timer = null;
    brand.addEventListener('click', function (e) {
      if (e.button !== 0) return;
      e.preventDefault();
      clicks += 1;
      clearTimeout(timer);
      timer = setTimeout(function () {
        clicks = 0;
      }, 800);
      if (clicks >= 3) {
        clicks = 0;
        showPasswordModal(function () {
          var host = document.getElementById('si-admin-host');
          if (!host || host.dataset.mounted === '1') return;
          host.dataset.mounted = '1';
          buildAdminPanel(host, data);
        });
      }
    });
  }

  if (!window.__SI_TAG_DELEGATION) {
    window.__SI_TAG_DELEGATION = true;
    document.addEventListener('click', function (e) {
      var btn = e.target && e.target.closest && e.target.closest('.tag-next');
      if (!btn) return;
      e.preventDefault();
      var targetId = btn.getAttribute('data-target');
      var scroller = document.getElementById(targetId);
      if (scroller) scroller.scrollBy({ left: 180, behavior: 'smooth' });
    });
  }

  function init() {
    var node = document.getElementById('report-initial-data');
    if (!node || !node.textContent) return;
    var data;
    try {
      data = JSON.parse(node.textContent);
    } catch (e) {
      return;
    }
    ensureNewFeaturesShape(data);
    var storageKey = STORAGE_PREFIX + data.reportId;
    var hadSaved = false;
    try {
      hadSaved = !!localStorage.getItem(storageKey);
    } catch (e2) {}
    data = loadStorageMerge(data);
    window.__SI_REPORT_DATA__ = data;
    if (hadSaved) renderAll(data);
    setupBrandUnlock(data);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
