"""Sinh một file HTML báo cáo bảo mật tổng hợp (RSS): nhiều section, i18n, bilingual."""

import html
import json
import os
import re
from typing import Any, Dict, List, Optional

from config.settings import DURATION, NOW, OUTPUT_PATH, TODAY
from core.ai_processor import AIProcessor
from core.logger import logger
from utils.time_utils import format_published
from config.settings import *

I18N_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config", "export_i18n.json"))
FULL_REPORT_ADMIN_JS_PATH = os.path.join(os.path.dirname(__file__), "full_report_admin.js")


def _load_i18n() -> Dict[str, Any]:
    try:
        with open(I18N_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def _i18n_text(i18n: Dict[str, Any], key: str, lang: str, default: str = "") -> str:
    value: Any = i18n
    for part in key.split("."):
        if not isinstance(value, dict):
            return default
        value = value.get(part)
    if isinstance(value, dict):
        return str(value.get(lang, value.get("en", default)))
    if isinstance(value, str):
        return value
    return default


def _lang_pack(lang: str):
    bilingual = lang.lower() in {"bilingual", "both", "bi"}
    default_lang = "vi" if bilingual else ("en" if lang.lower() == "en" else "vi")
    return bilingual, default_lang


def _dual_text(vi_text: str, en_text: str, bilingual: bool, default_lang: str) -> str:
    if not bilingual:
        return html.escape(vi_text if default_lang == "vi" else en_text)
    vi_style = "" if default_lang == "vi" else ' style="display:none"'
    en_style = "" if default_lang == "en" else ' style="display:none"'
    return (
        f'<span class="lang-vi"{vi_style}>{html.escape(vi_text)}</span>'
        f'<span class="lang-en"{en_style}>{html.escape(en_text)}</span>'
    )


def _dual_i18n(i18n: Dict[str, Any], key: str, bilingual: bool, default_lang: str, fallback_vi: str, fallback_en: str) -> str:
    vi_text = _i18n_text(i18n, key, "vi", fallback_vi)
    en_text = _i18n_text(i18n, key, "en", fallback_en)
    return _dual_text(vi_text, en_text, bilingual, default_lang)


def _title_html(item: Dict[str, Any], idx: int) -> str:
    title = html.escape(item.get("title", "No Title"))
    link = item.get("link", "")
    return f'{idx}. <a href="{html.escape(link)}" target="_blank" rel="noopener noreferrer">{title}</a>' if link else f"{idx}. {title}"


def _summary(item: Dict[str, Any], lang: str) -> str:
    return html.escape(item.get("summary_vi", "") if lang == "vi" else item.get("summary_en", ""))


def _item_tags(item: Dict[str, Any]) -> List[str]:
    raw_tags = item.get("tags", [])
    if isinstance(raw_tags, list):
        return [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    return []


def _item_tags_json_attr(item: Dict[str, Any]) -> str:
    return html.escape(json.dumps(_item_tags(item), ensure_ascii=False))


def _item_image(item: Dict[str, Any]) -> str:
    image_url = item.get("image", "https://ciso.economictimes.indiatimes.com/news/ciso-strategies/cyber-attacks-on-manufacturers-up-globally-but-less-than-half-prepared-in-security-omdia/118546241")
    return str(image_url).strip() if image_url else ""


def _image_or_placeholder(item: Dict[str, Any], css_class: str, fallback_gradient: str) -> str:
    image_url = _item_image(item)
    if image_url:
        return f'<img src="{html.escape(image_url)}" alt="article image" class="{css_class}" referrerpolicy="no-referrer"/>'
    return f'<div class="{css_class} {fallback_gradient}"></div>'


def _clean_description(raw_value: Any) -> str:
    if raw_value is None:
        return ""
    text = html.unescape(str(raw_value))
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(
        r"The post\s+.*?\s+appeared first on\s+.*?(?:\.|$)",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _overview_plain_pair(data: List[Dict[str, Any]]) -> tuple[str, str]:
    if not data:
        return ("", "")
    ai = AIProcessor()

    if IS_TEST_AI_PROCESS:
        return (
            ai.summarize_overview_sample_vi(data) or "",
            ai.summarize_overview_sample_en(data) or "",
        )

    return (
        ai.summarize_overview_gauss_vi(data) or "",
        ai.summarize_overview_gauss_en(data) or "",
    )


def _render_tag_filter_shell(
    i18n: Dict[str, Any], bilingual: bool, default_lang: str, element_id: str = ""
) -> str:
    id_attr = f' id="{html.escape(element_id)}"' if element_id else ""
    label = _dual_i18n(i18n, "labels.filter_by_tag", bilingual, default_lang, "Loc theo tag", "Filter by tag")
    return f"""<div class="report-tag-filter mb-6"{id_attr}>
        <div class="mb-2 text-xs font-bold text-[#414755] uppercase tracking-wider">{label}</div>
        <div class="report-tag-filter-chips flex flex-wrap gap-2">
            <div class="report-tag-filter-chips-primary contents"></div>
            <div class="report-tag-filter-chips-extra contents hidden"></div>
        </div>
        <button type="button" class="report-tag-filter-toggle hidden text-sm font-semibold text-[#0052d1] mt-1 hover:underline cursor-pointer bg-transparent border-0 p-0 font-inherit" aria-expanded="false"></button>
    </div>"""


def _render_overview_block(overview_html: str, i18n: Dict[str, Any], bilingual: bool, default_lang: str) -> str:
    if not overview_html:
        return ""
    return f"""
        <article class="bg-white rounded-lg p-6 border border-[#e1e3e4]">
            <div class="flex items-center gap-2 mb-2 text-[#0052d1] font-bold text-xs uppercase tracking-widest">
                <span class="material-symbols-outlined text-base" style="font-variation-settings: 'FILL' 1;">auto_stories</span>
                {_dual_i18n(i18n, "labels.overall", bilingual, default_lang, "Tong quan", "Overall")}
            </div>
            <p class="text-[#414755] leading-relaxed">{overview_html}</p>
        </article>
    """


def _render_global_information(
    data: List[Dict[str, Any]], i18n: Dict[str, Any], lang: str, bilingual: bool, default_lang: str
) -> str:
    cards = ""
    for idx, item in enumerate(data, start=1):
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(_clean_description(item.get("snippet", "")))
        if len(snippet) > 1000: 
            snippet = snippet[:1000] + "..."
        tags = _item_tags(item)
        tag_items = tags if tags else [_i18n_text(i18n, "labels.security", default_lang, "Security")]
        tags_html = "".join(
            f'<span class="bg-[#90efef] text-[#006e6e] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider whitespace-nowrap">{html.escape(tag)}</span>'
            for tag in tag_items
        )
        tag_scroller_id = f"tagScrollerGI{idx}"
        tags_json = _item_tags_json_attr(item)
        image_html = _image_or_placeholder(
            item,
            "w-full h-56 object-cover rounded-lg",
            "bg-gradient-to-br from-[#dae1ff] to-[#b3c5ff]",
        )
        cards += f"""
        <article class="bg-white rounded-lg p-6 group transition-all hover:bg-[#edeeef] report-article-filterable" data-item-tags="{tags_json}">
            <div class="flex flex-col gap-4">
                <div>{image_html}</div>
                <div>
                    <h2 class="text-2xl font-bold text-[#0052d1] group-hover:text-[#156aff] transition-colors">{_title_html(item, idx)}</h2>
                    <div class="mt-2 flex items-center gap-2">
                        <div id="{tag_scroller_id}" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1">
                            {tags_html}
                        </div>
                        <button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="{tag_scroller_id}">&gt;</button>
                    </div>
                </div>
                <div class="flex items-center gap-4 text-[#414755] text-sm font-semibold">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">calendar_today</span>{published}</span>
                </div>
                <p class="text-[#414755] leading-relaxed">{snippet}</p>
                <div class="mt-2 p-5 bg-[#93f2f2]/20 border-l-4 border-[#006a6a] rounded-r-lg">
                    <div class="flex items-center gap-2 mb-2 text-[#006a6a] font-bold text-xs uppercase tracking-widest">
                        <span class="material-symbols-outlined text-lg" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
                        {_dual_i18n(i18n, "labels.summary_ai_curator", bilingual, default_lang, "Tom tat AI", "AI Curator Summary")}
                    </div>
                    <p class="text-[#004f4f] text-sm font-medium italic">
                        {_dual_text(item.get("summary_vi", ""), item.get("summary_en", ""), bilingual, default_lang)}
                    </p>
                </div>
            </div>
        </article>
        """
    return cards or '<p class="text-[#414755] italic">No data.</p>'


def _render_new_features_cards(
    data: List[Dict[str, Any]],
    i18n: Dict[str, Any],
    lang: str,
    bilingual: bool,
    default_lang: str,
    panel_id: str = "",
) -> str:
    cards = ""
    for idx, item in enumerate(data, start=1):
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(_clean_description(item.get("snippet", "")))
        if len(snippet) > 1000: 
            snippet = snippet[:1000] + "..."
        feature_badge = _dual_i18n(i18n, "labels.feature_badge", bilingual, default_lang, "Tinh nang", "Feature")
        tags = _item_tags(item)
        tag_items = tags if tags else [_i18n_text(i18n, "labels.security", default_lang, "Security")]
        tags_html = "".join(
            f'<span class="bg-[#90efef] text-[#006e6e] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider whitespace-nowrap">{html.escape(tag)}</span>'
            for tag in tag_items
        )
        tag_scroller_id = f"tagScrollerNF{panel_id}{idx}" if panel_id else f"tagScrollerNF{idx}"
        tags_json = _item_tags_json_attr(item)
        media_html = _image_or_placeholder(
            item,
            "w-full h-full object-cover rounded-lg",
            "bg-gradient-to-br from-[#c1c6d7] to-[#e1e3e4]",
        )
        cards += f"""
        <article class="flex flex-col md:flex-row gap-8 bg-white p-6 rounded-lg transition-all hover:bg-[#edeeef] report-article-filterable" data-item-tags="{tags_json}">
            <div class="w-full md:w-1/3 aspect-video overflow-hidden rounded-lg">
                {media_html}
            </div>
            <div class="flex-1 flex flex-col justify-center">
                <div class="flex items-center gap-3 mb-3">
                    <span class="text-[10px] font-black text-[#006a6a] tracking-widest uppercase">{feature_badge}</span>
                    <span class="text-[10px] font-medium text-[#414755]/70 uppercase">{published}</span>
                </div>
                <h4 class="text-2xl font-extrabold text-[#191c1d] mb-3 tracking-tight">{_title_html(item, idx)}</h4>
                <div class="mb-3 flex items-center gap-2">
                    <div id="{tag_scroller_id}" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1 flex-wrap">
                        {tags_html}
                    </div>
                    <button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="{tag_scroller_id}">&gt;</button>
                </div>
                <p class="text-[#414755] text-base mb-6 leading-relaxed">{snippet}</p>
                <div class="bg-[#93f2f2]/20 p-4 rounded-lg border-l-4 border-[#006a6a]">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="material-symbols-outlined text-[#006a6a] text-sm" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
                        <span class="text-[10px] font-black text-[#006a6a] uppercase tracking-tight">{_dual_i18n(i18n, "labels.summary_curator", bilingual, default_lang, "Tom tat AI", "Curator AI Summary")}</span>
                    </div>
                    <p class="text-xs text-[#004f4f] leading-normal">
                        {_dual_text(item.get("summary_vi", ""), item.get("summary_en", ""), bilingual, default_lang)}
                    </p>
                </div>
            </div>
        </article>
        """
    return cards or '<p class="text-[#414755] italic">No data.</p>'


def _render_new_features_grouped(
    samsung_data: List[Dict[str, Any]],
    iphone_data: List[Dict[str, Any]],
    china_data: List[Dict[str, Any]],
    i18n: Dict[str, Any],
    lang: str,
    bilingual: bool,
    default_lang: str,
) -> str:
    triples: List[tuple[str, List[Dict[str, Any]], str, str, str]] = [
        ("nfSamsung", samsung_data, "subsections.new_features_samsung", "Samsung", "Samsung"),
        ("nfIphone", iphone_data, "subsections.new_features_iphone", "iPhone", "iPhone"),
        (
            "nfChina",
            china_data,
            "subsections.new_features_china",
            "Trung Quoc (hang dien thoai)",
            "China (Chinese phone brands)",
        ),
    ]
    pills: List[str] = []
    panels: List[str] = []
    for idx, (panel_id, data, i18n_key, fv, fe) in enumerate(triples):
        label_html = _dual_i18n(i18n, i18n_key, bilingual, default_lang, fv, fe)
        is_first = idx == 0
        pill_cls = "nf-pill nf-pill-active" if is_first else "nf-pill nf-pill-idle"
        aria_sel = "true" if is_first else "false"
        pills.append(
            f'<button type="button" class="{pill_cls} px-5 py-2 rounded-full text-sm font-semibold transition-all" '
            f'data-nf-target="{panel_id}" role="tab" aria-selected="{aria_sel}">{label_html}</button>'
        )
        cards_html = _render_new_features_cards(data, i18n, lang, bilingual, default_lang, panel_id)
        ov_vi, ov_en = _overview_plain_pair(data)
        overview_inner = _dual_text(ov_vi, ov_en, bilingual, default_lang) if (ov_vi or ov_en) else ""
        overview_block = _render_overview_block(overview_inner, i18n, bilingual, default_lang) if overview_inner else ""
        overview_wrap = f'<div class="mb-8">{overview_block}</div>' if overview_block else ""
        panel_open = " new-features-subpanel-open" if is_first else ""
        filter_shell = _render_tag_filter_shell(
            i18n, bilingual, default_lang, f"report-tag-filter-{panel_id}"
        )
        panels.append(
            f"""
        <div id="{panel_id}" class="new-features-subpanel space-y-6{panel_open}" role="tabpanel" aria-hidden="{'false' if is_first else 'true'}">
            {overview_wrap}
            <div class="report-tag-scope space-y-6">
                {filter_shell}
                <div class="space-y-8">{cards_html}</div>
            </div>
        </div>
        """
        )
    subnav = (
        f'<div class="flex flex-wrap gap-3 mb-8" id="new-features-subnav" role="tablist">'
        f'{"".join(pills)}'
        f"</div>"
    )
    stack = f'<div id="report-new-features-panels" class="relative">{"".join(panels)}</div>'
    return f"{subnav}{stack}"


def _render_hot_like(
    data: List[Dict[str, Any]],
    i18n: Dict[str, Any],
    lang: str,
    badge_vi: str,
    badge_en: str,
    bilingual: bool,
    default_lang: str,
    tag_scroller_prefix: str = "hl",
) -> str:
    cards = ""
    for idx, item in enumerate(data, start=1):
        published = html.escape(format_published(item.get("published", "")))
        snippet = html.escape(_clean_description(item.get("snippet", "")))
        if len(snippet) > 1000: 
            snippet = snippet[:1000] + "..."
        tags = _item_tags(item)
        tag_items = tags if tags else [_i18n_text(i18n, "labels.security", default_lang, "Security")]
        tags_html = "".join(
            f'<span class="bg-[#90efef] text-[#006e6e] px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider whitespace-nowrap">{html.escape(tag)}</span>'
            for tag in tag_items
        )
        tag_scroller_id = f"tagScroller{tag_scroller_prefix}{idx}"
        tags_json = _item_tags_json_attr(item)
        media_html = _image_or_placeholder(
            item,
            "w-full h-48 object-cover rounded-lg",
            "bg-gradient-to-br from-[#dae1ff] to-[#b3c5ff]",
        )
        cards += f"""
        <article class="group bg-white rounded-lg p-6 lg:p-8 flex flex-col lg:flex-row gap-8 transition-transform hover:scale-[1.01] duration-300 report-article-filterable" data-item-tags="{tags_json}">
            <div class="lg:w-1/3 shrink-0">
                {media_html}
            </div>
            <div class="flex-1 flex flex-col">
                <div class="flex items-center gap-3 mb-3">
                    <span class="bg-[#ffdad6] text-[#93000a] text-[10px] px-2 py-1 font-black uppercase tracking-tighter rounded-sm">{_dual_text(badge_vi, badge_en, bilingual, default_lang)}</span>
                    <span class="text-[#414755] text-xs font-medium uppercase tracking-widest">{published}</span>
                </div>
                <h2 class="font-headline font-bold text-2xl text-[#191c1d] mb-3 group-hover:text-[#0052d1] transition-colors">{_title_html(item, idx)}</h2>
                <div class="mb-4 flex items-center gap-2">
                    <div id="{tag_scroller_id}" class="tag-scroller flex gap-2 overflow-x-auto no-scrollbar pr-1 flex-wrap">
                        {tags_html}
                    </div>
                    <button type="button" class="tag-next hidden text-[#0052d1] font-bold px-2 py-1 rounded border border-[#c1c6d7]" data-target="{tag_scroller_id}">&gt;</button>
                </div>
                <p class="text-[#414755] leading-relaxed mb-6">{snippet}</p>
                <div class="bg-[#93f2f2]/20 p-4 rounded-lg border-l-4 border-[#006a6a] flex items-start gap-4">
                    <span class="material-symbols-outlined text-[#006a6a] text-xl">auto_awesome</span>
                    <div>
                        <p class="text-xs font-bold text-[#006a6a] uppercase tracking-widest mb-1">{_dual_i18n(i18n, "labels.summary_ai_intel", bilingual, default_lang, "Tom tat AI", "AI Intelligence Summary")}</p>
                        <p class="text-sm text-[#191c1d] leading-tight font-medium">
                            {_dual_text(item.get("summary_vi", ""), item.get("summary_en", ""), bilingual, default_lang)}
                        </p>
                    </div>
                </div>
            </div>
        </article>
        """
    return cards or '<p class="text-[#414755] italic">No data.</p>'


def _client_labels_bundle(i18n: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    def pair(key: str, fallback_vi: str, fallback_en: str) -> Dict[str, str]:
        return {
            "vi": _i18n_text(i18n, key, "vi", fallback_vi),
            "en": _i18n_text(i18n, key, "en", fallback_en),
        }

    return {
        "overall": pair("labels.overall", "Tong quan", "Overall"),
        "security": pair("labels.security", "Security", "Security"),
        "feature_badge": pair("labels.feature_badge", "Tinh nang", "Feature"),
        "issue_badge": pair("labels.issue_badge", "Van de", "Issue"),
        "patent_badge": pair("labels.patent_badge", "Bang sang che", "Patent"),
        "summary_ai_curator": pair("labels.summary_ai_curator", "Tom tat AI", "AI Curator Summary"),
        "summary_curator": pair("labels.summary_curator", "Tom tat AI", "Curator AI Summary"),
        "summary_ai_intel": pair("labels.summary_ai_intel", "Tom tat AI", "AI Intelligence Summary"),
        "no_data": pair("labels.no_data", "Khong co du lieu.", "No data."),
        "new_features_samsung": pair("subsections.new_features_samsung", "Samsung", "Samsung"),
        "new_features_iphone": pair("subsections.new_features_iphone", "iPhone", "iPhone"),
        "new_features_china": pair("subsections.new_features_china", "Trung Quoc", "China"),
        "filter_by_tag": pair("labels.filter_by_tag", "Loc theo tag", "Filter by tag"),
        "show_more_tags": pair("labels.show_more_tags", "Xem thêm ({n})", "Show more ({n})"),
        "show_less_tags": pair("labels.show_less_tags", "Thu gọn", "Show less"),
    }


def _json_for_html_script(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False).replace("</", "\\u003c/")


def _read_full_report_admin_js() -> str:
    try:
        with open(FULL_REPORT_ADMIN_JS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        logger.warning("[EXPORT] Không đọc được full_report_admin.js — chức năng quản trị HTML bị tắt.")
        return ""


def export_full_security_report_html(
    global_information_data: List[Dict[str, Any]],
    service: str,
    new_features_samsung_data: Optional[List[Dict[str, Any]]] = None,
    new_features_iphone_data: Optional[List[Dict[str, Any]]] = None,
    new_features_china_data: Optional[List[Dict[str, Any]]] = None,
    hot_android_issues_data: Optional[List[Dict[str, Any]]] = None,
    patent_trend_data: Optional[List[Dict[str, Any]]] = None,
    lang: str = "vi",
):
    """Gộp nhiều luồng RSS thành một HTML: global, new features (3 nhóm), hot issues, patent trend.

    Tham số `*_data` tùy chọn: None thì fallback sang `global_information_data` hoặc
    dữ liệu mặc định theo logic trong hàm. `lang`: "vi" | "en" | "bilingual".
    """
    i18n = _load_i18n()
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    _nf_default = global_information_data
    new_features_samsung_data = new_features_samsung_data if new_features_samsung_data is not None else _nf_default
    new_features_iphone_data = new_features_iphone_data if new_features_iphone_data is not None else _nf_default
    new_features_china_data = new_features_china_data if new_features_china_data is not None else _nf_default
    hot_android_issues_data = hot_android_issues_data if hot_android_issues_data is not None else global_information_data
    patent_trend_data = patent_trend_data if patent_trend_data is not None else global_information_data

    filepath = os.path.join(
        OUTPUT_PATH,
        f"results_{NOW}_{DURATION}days_{service}_FULL_REPORT_{'VI' if lang == 'vi' else 'EN'}.html",
    )

    bilingual, default_lang = _lang_pack(lang)
    suffix = "BILINGUAL" if bilingual else ("EN" if default_lang == "en" else "VI")
    filepath = os.path.join(
        OUTPUT_PATH,
        f"results_{NOW}_{DURATION}days_{service}_FULL_REPORT_{suffix}.html",
    )

    title = _dual_i18n(i18n, "report.title", bilingual, default_lang, "Bao cao tong hop bao mat", "Security Intelligence Full Report")
    updated_vi_tpl = _i18n_text(i18n, "report.updated", "vi", "Ngay {today} - {duration} ngay gan nhat")
    updated_en_tpl = _i18n_text(i18n, "report.updated", "en", "Updated at {today} - Last {duration} days")
    updated = _dual_text(
        updated_vi_tpl.format(today=TODAY, duration=DURATION),
        updated_en_tpl.format(today=TODAY, duration=DURATION),
        bilingual,
        default_lang,
    )

    section_global = _render_global_information(global_information_data, i18n, default_lang, bilingual, default_lang)
    section_features = _render_new_features_grouped(
        new_features_samsung_data,
        new_features_iphone_data,
        new_features_china_data,
        i18n,
        default_lang,
        bilingual,
        default_lang,
    )
    section_hot = _render_hot_like(
        hot_android_issues_data,
        i18n,
        default_lang,
        _i18n_text(i18n, "labels.issue_badge", "vi", "Van de"),
        _i18n_text(i18n, "labels.issue_badge", "en", "Issue"),
        bilingual,
        default_lang,
        "Hot",
    )
    section_patent = _render_hot_like(
        patent_trend_data,
        i18n,
        default_lang,
        _i18n_text(i18n, "labels.patent_badge", "vi", "Bang sang che"),
        _i18n_text(i18n, "labels.patent_badge", "en", "Patent"),
        bilingual,
        default_lang,
        "Patent",
    )
    og_vi, og_en = _overview_plain_pair(global_information_data)
    nf_s_vi, nf_s_en = _overview_plain_pair(new_features_samsung_data)
    nf_i_vi, nf_i_en = _overview_plain_pair(new_features_iphone_data)
    nf_c_vi, nf_c_en = _overview_plain_pair(new_features_china_data)
    hot_vi, hot_en = _overview_plain_pair(hot_android_issues_data)
    pt_vi, pt_en = _overview_plain_pair(patent_trend_data)

    overview_global = _render_overview_block(
        _dual_text(og_vi, og_en, bilingual, default_lang) if (og_vi or og_en) else "",
        i18n,
        bilingual,
        default_lang,
    )
    overview_hot = _render_overview_block(
        _dual_text(hot_vi, hot_en, bilingual, default_lang) if (hot_vi or hot_en) else "",
        i18n,
        bilingual,
        default_lang,
    )
    overview_patent = _render_overview_block(
        _dual_text(pt_vi, pt_en, bilingual, default_lang) if (pt_vi or pt_en) else "",
        i18n,
        bilingual,
        default_lang,
    )

    tag_filter_global = _render_tag_filter_shell(
        i18n, bilingual, default_lang, "report-tag-filter-globalInformation"
    )
    tag_filter_hot = _render_tag_filter_shell(
        i18n, bilingual, default_lang, "report-tag-filter-hotAndroidIssues"
    )
    tag_filter_patent = _render_tag_filter_shell(
        i18n, bilingual, default_lang, "report-tag-filter-patentTrend"
    )

    report_storage_key = f"{NOW}_{DURATION}d_{service}_{suffix}"
    report_payload: Dict[str, Any] = {
        "reportId": report_storage_key,
        "bilingual": bilingual,
        "defaultLang": default_lang,
        "labels": _client_labels_bundle(i18n),
        "modules": {
            "globalInformation": global_information_data,
            "newFeatures": {
                "samsung": new_features_samsung_data,
                "iphone": new_features_iphone_data,
                "china": new_features_china_data,
            },
            "hotAndroidIssues": hot_android_issues_data,
            "patentTrend": patent_trend_data,
        },
        "overviews": {
            "globalInformation": {"vi": og_vi, "en": og_en},
            "newFeatures": {
                "samsung": {"vi": nf_s_vi, "en": nf_s_en},
                "iphone": {"vi": nf_i_vi, "en": nf_i_en},
                "china": {"vi": nf_c_vi, "en": nf_c_en},
            },
            "hotAndroidIssues": {"vi": hot_vi, "en": hot_en},
            "patentTrend": {"vi": pt_vi, "en": pt_en},
        },
    }
    report_json = _json_for_html_script(report_payload)
    admin_js = _read_full_report_admin_js()

    html_content = f"""<!DOCTYPE html>
<html lang="{'vi' if lang == 'vi' else 'en'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="report-storage-key" content="{html.escape(report_storage_key)}">
    <title>Security Insights</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }}
        body {{ font-family: 'Inter', sans-serif; }}
        h1, h2, h3, h4 {{ font-family: 'Manrope', sans-serif; }}
        .module {{ display: none; }}
        .module.active {{ display: block; }}
        .module-tab.active {{ color: #0052d1; border-bottom: 2px solid #0052d1; }}
        .new-features-subpanel {{ display: none; }}
        .new-features-subpanel.new-features-subpanel-open {{ display: block; }}
        .nf-pill {{ border: none; cursor: pointer; font-family: inherit; }}
        .nf-pill-active {{ background-color: #90efef; color: #006e6e; }}
        .nf-pill-idle {{ background-color: #e7e8e9; color: #414755; }}
        .nf-pill-idle:hover {{ background-color: #edeeef; }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        #si-admin-host {{ font-family: 'Inter', system-ui, sans-serif; }}
        #si-admin-host * {{ box-sizing: border-box; }}
        .report-tag-chip {{ border: 1px solid #c1c6d7; background: #fff; color: #414755; border-radius: 999px; padding: 4px 12px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit; transition: background .15s, color .15s, border-color .15s; }}
        .report-tag-chip:hover {{ background: #edeeef; }}
        .report-tag-chip.si-tag-selected {{ background-color: #90efef; color: #006e6e; border-color: #006e6e; }}
    </style>
    <script id="report-initial-data" type="application/json">{report_json}</script>
</head>
<body class="bg-[#f8f9fa] text-[#191c1d]">
    <header class="fixed top-0 w-full z-50 bg-[#ffffff]/80 backdrop-blur-md shadow-[0_40px_40px_rgba(25,28,29,0.04)] h-20">
        <div class="flex justify-between items-center w-full px-8 h-full max-w-[1440px] mx-auto">
            <div class="text-2xl font-extrabold tracking-tighter"><span id="report-brand-unlock" class="inline-block cursor-default select-none" title="">{_dual_i18n(i18n, "report.brand", bilingual, default_lang, "Security Insights", "Security Insights")}</span></div>
            <nav class="hidden md:flex gap-8 items-center h-full">
                <button class="module-tab active pb-1 font-bold text-lg tracking-tight" data-target="globalInformation">{_dual_i18n(i18n, "nav.global_information", bilingual, default_lang, "Thong tin toan cau", "Global Information")}</button>
                <button class="module-tab text-[#414755] font-medium text-lg tracking-tight" data-target="newFeatures">{_dual_i18n(i18n, "nav.new_features", bilingual, default_lang, "Tinh nang moi", "New Features")}</button>
                <button class="module-tab text-[#414755] font-medium text-lg tracking-tight" data-target="hotAndroidIssues">{_dual_i18n(i18n, "nav.hot_android_issues", bilingual, default_lang, "Van de Android noi bat", "Hot Android Issues")}</button>
                <button class="module-tab text-[#414755] font-medium text-lg tracking-tight" data-target="patentTrend">{_dual_i18n(i18n, "nav.patent_trend", bilingual, default_lang, "Xu huong bang sang che", "Security Patent Trend")}</button>
            </nav>
            <div class="text-sm text-[#414755]">{updated}</div>
        </div>
    </header>
    <div class="flex min-h-screen pt-20">
        <main class="flex-1 p-8 max-w-5xl mx-auto w-full">
            {"<div class='mb-6 flex gap-2'><button id='lang-vi-btn' class='px-3 py-1 rounded border border-[#c1c6d7]'>VI</button><button id='lang-en-btn' class='px-3 py-1 rounded border border-[#c1c6d7]'>EN</button></div>" if bilingual else ""}
            <section id="globalInformation" class="module active">
                <header class="mb-8">
                    <h1 class="text-4xl font-extrabold tracking-tight mb-2">{_dual_i18n(i18n, "sections.global_information.title", bilingual, default_lang, "Thong tin toan cau", "Global Information")}</h1>
                    <p class="text-[#414755] text-lg max-w-2xl">{_dual_i18n(i18n, "sections.global_information.description", bilingual, default_lang, "Tong hop tin tuc an ninh theo ngay.", "Daily curated security intelligence from the bedrock of the digital landscape.")}</p>
                </header>
                <div id="report-overview-globalInformation" class="mb-8">{overview_global}</div>
                <div class="report-tag-scope">
                    {tag_filter_global}
                    <div id="report-list-globalInformation" class="space-y-8">{section_global}</div>
                </div>
            </section>

            <section id="newFeatures" class="module">
                <header class="mb-8">
                    <h1 class="text-4xl font-extrabold tracking-tight mb-2">{_dual_i18n(i18n, "sections.new_features.title", bilingual, default_lang, "Tinh nang moi", "New Features")}</h1>
                    <p class="text-[#414755] text-lg max-w-2xl">{_dual_i18n(i18n, "sections.new_features.description", bilingual, default_lang, "Cap nhat tinh nang va huong phat trien san pham.", "Editorial updates for upcoming products, platform releases, and feature trends.")}</p>
                </header>
                <div id="report-new-features-root" class="space-y-0">{section_features}</div>
            </section>

            <section id="hotAndroidIssues" class="module">
                <header class="mb-8">
                    <h1 class="text-4xl font-extrabold tracking-tight mb-2">{_dual_i18n(i18n, "sections.hot_android_issues.title", bilingual, default_lang, "Van de Android noi bat", "Hot Android Issues")}</h1>
                    <p class="text-[#414755] text-lg max-w-2xl">{_dual_i18n(i18n, "sections.hot_android_issues.description", bilingual, default_lang, "Loi nghiem trong va canh bao bao mat Android.", "Critical vulnerabilities, exploit signals, and urgent Android security advisories.")}</p>
                </header>
                <div id="report-overview-hotAndroidIssues" class="mb-8">{overview_hot}</div>
                <div class="report-tag-scope">
                    {tag_filter_hot}
                    <div id="report-list-hotAndroidIssues" class="space-y-6">{section_hot}</div>
                </div>
            </section>

            <section id="patentTrend" class="module">
                <header class="mb-8">
                    <h1 class="text-4xl font-extrabold tracking-tight mb-2">{_dual_i18n(i18n, "sections.patent_trend.title", bilingual, default_lang, "Xu huong bang sang che", "Patent Trend")}</h1>
                    <p class="text-[#414755] text-lg max-w-2xl">{_dual_i18n(i18n, "sections.patent_trend.description", bilingual, default_lang, "Tin hieu xu huong bao mat qua du lieu bang sang che.", "Patent-driven signals about where mobile security capabilities are moving next.")}</p>
                </header>
                <div id="report-overview-patentTrend" class="mb-8">{overview_patent}</div>
                <div class="report-tag-scope">
                    {tag_filter_patent}
                    <div id="report-list-patentTrend" class="space-y-6">{section_patent}</div>
                </div>
            </section>
        </main>
    </div>
    <div id="si-admin-host"></div>
    <script>
        const tabs = document.querySelectorAll('.module-tab');
        const modules = document.querySelectorAll('.module');
        tabs.forEach((tab) => {{
            tab.addEventListener('click', () => {{
                const target = tab.getAttribute('data-target');
                tabs.forEach((t) => {{
                    t.classList.remove('active');
                    t.classList.add('text-[#414755]');
                }});
                tab.classList.add('active');
                tab.classList.remove('text-[#414755]');
                modules.forEach((module) => {{
                    module.classList.toggle('active', module.id === target);
                }});
            }});
        }});
        function initTagScrollers() {{
            document.querySelectorAll('.tag-next').forEach((button) => {{
                const targetId = button.getAttribute('data-target');
                const scroller = document.getElementById(targetId);
                if (!scroller) return;
                const hasOverflow = scroller.scrollWidth > scroller.clientWidth + 2;
                button.classList.toggle('hidden', !hasOverflow);
                button.addEventListener('click', () => {{
                    scroller.scrollBy({{ left: 180, behavior: 'smooth' }});
                }});
            }});
        }}
        initTagScrollers();
        function siGetReportTagFilterLabels(langOverride) {{
            var showMoreTpl = 'Show more ({{n}})';
            var showLess = 'Show less';
            try {{
                var el = document.getElementById('report-initial-data');
                if (!el || !el.textContent) return {{ showMoreTpl: showMoreTpl, showLess: showLess }};
                var d = JSON.parse(el.textContent);
                var lang = langOverride;
                if (lang !== 'vi' && lang !== 'en') {{
                    lang = d.defaultLang === 'en' ? 'en' : 'vi';
                }}
                var L = d.labels || {{}};
                if (L.show_more_tags && typeof L.show_more_tags === 'object') {{
                    showMoreTpl = (lang === 'vi' ? L.show_more_tags.vi : L.show_more_tags.en) || showMoreTpl;
                }}
                if (L.show_less_tags && typeof L.show_less_tags === 'object') {{
                    showLess = (lang === 'vi' ? L.show_less_tags.vi : L.show_less_tags.en) || showLess;
                }}
            }} catch (e) {{}}
            return {{ showMoreTpl: showMoreTpl, showLess: showLess }};
        }}
        function siEnsureReportUiLang() {{
            if (window.__SI_currentLang === 'vi' || window.__SI_currentLang === 'en') return;
            try {{
                var el = document.getElementById('report-initial-data');
                if (el && el.textContent) {{
                    var d = JSON.parse(el.textContent);
                    window.__SI_currentLang = d.defaultLang === 'en' ? 'en' : 'vi';
                }} else {{
                    window.__SI_currentLang = 'vi';
                }}
            }} catch (e2) {{
                window.__SI_currentLang = 'vi';
            }}
        }}
        window.__SI_refreshTagFilterToggles = function (lang) {{
            siEnsureReportUiLang();
            if (lang === 'vi' || lang === 'en') window.__SI_currentLang = lang;
            var lbl = siGetReportTagFilterLabels(window.__SI_currentLang);
            document.querySelectorAll('.report-tag-filter-toggle').forEach(function (btn) {{
                if (btn.classList.contains('hidden')) return;
                var extra = parseInt(btn.getAttribute('data-extra-count') || '0', 10);
                if (!extra) return;
                var expanded = btn.getAttribute('data-expanded') === 'true';
                btn.textContent = expanded
                    ? lbl.showLess
                    : lbl.showMoreTpl.replace(/\\{{n\\}}/g, String(extra));
            }});
        }};
        function initReportTagFilters(root) {{
            root = root || document;
            siEnsureReportUiLang();
            var MAX_TAG_FILTER_CHIPS_VISIBLE = 10;
            root.querySelectorAll('.report-tag-scope').forEach(function (scope) {{
                var filterHost = scope.querySelector('.report-tag-filter');
                if (!filterHost) return;
                var primaryEl = filterHost.querySelector('.report-tag-filter-chips-primary');
                var extraEl = filterHost.querySelector('.report-tag-filter-chips-extra');
                var toggleBtn = filterHost.querySelector('.report-tag-filter-toggle');
                if (!primaryEl || !extraEl || !toggleBtn) return;
                var articlesLive = function () {{
                    return scope.querySelectorAll('article.report-article-filterable');
                }};
                var tagMap = new Map();
                articlesLive().forEach(function (art) {{
                    var raw = art.getAttribute('data-item-tags');
                    if (!raw) return;
                    var tags;
                    try {{ tags = JSON.parse(raw); }} catch (e) {{ return; }}
                    if (!Array.isArray(tags)) return;
                    tags.forEach(function (t) {{
                        var s = String(t).trim();
                        if (!s) return;
                        var low = s.toLowerCase();
                        if (!tagMap.has(low)) tagMap.set(low, s);
                    }});
                }});
                var entries = Array.from(tagMap.entries()).sort(function (a, b) {{
                    return a[1].localeCompare(b[1], undefined, {{ sensitivity: 'base' }});
                }});
                primaryEl.innerHTML = '';
                extraEl.innerHTML = '';
                function appendChip(container, entry) {{
                    var low = entry[0];
                    var label = entry[1];
                    var btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'report-tag-chip';
                    btn.textContent = label;
                    btn.setAttribute('data-tag-key', low);
                    btn.setAttribute('aria-pressed', 'false');
                    container.appendChild(btn);
                }}
                var i = 0;
                for (; i < entries.length && i < MAX_TAG_FILTER_CHIPS_VISIBLE; i++) {{
                    appendChip(primaryEl, entries[i]);
                }}
                for (; i < entries.length; i++) {{
                    appendChip(extraEl, entries[i]);
                }}
                var extraCount = entries.length > MAX_TAG_FILTER_CHIPS_VISIBLE
                    ? entries.length - MAX_TAG_FILTER_CHIPS_VISIBLE
                    : 0;
                function setExpanded(expanded) {{
                    siEnsureReportUiLang();
                    toggleBtn.setAttribute('data-extra-count', String(extraCount));
                    if (extraCount === 0) {{
                        toggleBtn.classList.add('hidden');
                        extraEl.classList.add('hidden');
                        return;
                    }}
                    toggleBtn.classList.remove('hidden');
                    var lbl = siGetReportTagFilterLabels(window.__SI_currentLang);
                    if (expanded) {{
                        extraEl.classList.remove('hidden');
                        toggleBtn.setAttribute('aria-expanded', 'true');
                        toggleBtn.setAttribute('data-expanded', 'true');
                        toggleBtn.textContent = lbl.showLess;
                    }} else {{
                        extraEl.classList.add('hidden');
                        toggleBtn.setAttribute('aria-expanded', 'false');
                        toggleBtn.setAttribute('data-expanded', 'false');
                        toggleBtn.textContent = lbl.showMoreTpl.replace(/\\{{n\\}}/g, String(extraCount));
                    }}
                }}
                setExpanded(false);
                toggleBtn.onclick = function (e) {{
                    e.preventDefault();
                    e.stopPropagation();
                    var willExpand = extraEl.classList.contains('hidden');
                    setExpanded(willExpand);
                }};
                function applyFilter() {{
                    var selected = [];
                    filterHost.querySelectorAll('.report-tag-chip.si-tag-selected').forEach(function (b) {{
                        selected.push(b.getAttribute('data-tag-key'));
                    }});
                    articlesLive().forEach(function (art) {{
                        var raw = art.getAttribute('data-item-tags');
                        var tags = [];
                        if (raw) {{
                            try {{ tags = JSON.parse(raw) || []; }} catch (e) {{}}
                        }}
                        if (!Array.isArray(tags)) tags = [];
                        var lowerSet = tags.map(function (x) {{ return String(x).trim().toLowerCase(); }}).filter(Boolean);
                        var show = selected.length === 0 || selected.every(function (req) {{ return lowerSet.indexOf(req) >= 0; }});
                        art.hidden = !show;
                        art.style.display = show ? '' : 'none';
                    }});
                }}
                filterHost.onclick = function (e) {{
                    var chip = e.target && e.target.closest && e.target.closest('.report-tag-chip');
                    if (!chip || !filterHost.contains(chip)) return;
                    chip.classList.toggle('si-tag-selected');
                    chip.setAttribute('aria-pressed', chip.classList.contains('si-tag-selected') ? 'true' : 'false');
                    applyFilter();
                }};
                applyFilter();
            }});
        }}
        window.__SI_initReportTagFilters = initReportTagFilters;
        initReportTagFilters(document);
        (function initNewFeaturesSubnav() {{
            if (window.__SI_nfSubnavInit) return;
            window.__SI_nfSubnavInit = true;
            document.addEventListener('click', function (e) {{
                var pill = e.target.closest('.nf-pill');
                if (!pill) return;
                var root = pill.closest('#report-new-features-root');
                if (!root) return;
                var id = pill.getAttribute('data-nf-target');
                if (!id) return;
                e.preventDefault();
                var pills = root.querySelectorAll('.nf-pill');
                var panels = root.querySelectorAll('.new-features-subpanel');
                pills.forEach(function (p) {{
                    var on = p.getAttribute('data-nf-target') === id;
                    p.classList.toggle('nf-pill-active', on);
                    p.classList.toggle('nf-pill-idle', !on);
                    p.setAttribute('aria-selected', on ? 'true' : 'false');
                }});
                panels.forEach(function (panel) {{
                    var on = panel.id === id;
                    panel.classList.toggle('new-features-subpanel-open', on);
                    panel.setAttribute('aria-hidden', on ? 'false' : 'true');
                }});
            }});
        }})();
        {"const viBtn=document.getElementById('lang-vi-btn'); const enBtn=document.getElementById('lang-en-btn'); function switchLanguage(lang){window.__SI_currentLang=lang; if(typeof window.__SI_refreshTagFilterToggles==='function'){window.__SI_refreshTagFilterToggles(lang);} document.querySelectorAll('.lang-vi').forEach(e=>e.style.display=lang==='vi'?'':'none'); document.querySelectorAll('.lang-en').forEach(e=>e.style.display=lang==='en'?'':'none'); if(viBtn&&enBtn){viBtn.classList.toggle('bg-[#0052d1]',lang==='vi'); viBtn.classList.toggle('text-white',lang==='vi'); enBtn.classList.toggle('bg-[#0052d1]',lang==='en'); enBtn.classList.toggle('text-white',lang==='en');}} window.__SI_switchLanguage=switchLanguage; if(viBtn&&enBtn){viBtn.addEventListener('click',()=>switchLanguage('vi')); enBtn.addEventListener('click',()=>switchLanguage('en')); switchLanguage('" + default_lang + "');}" if bilingual else ""}
    </script>
</body>
</html>"""

    if admin_js:
        html_content = html_content.replace("</body>", "    <script>\n" + admin_js + "\n    </script>\n</body>")

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(html_content)

    logger.info(f"[EXPORT] Xuất báo cáo tổng hợp thành công ra {filepath}")
    return filepath


def export_rss_report_to_json(
    global_information_data: List[Dict[str, Any]],
    service: str,
    new_features_samsung_data: Optional[List[Dict[str, Any]]] = None,
    new_features_iphone_data: Optional[List[Dict[str, Any]]] = None,
    new_features_china_data: Optional[List[Dict[str, Any]]] = None,
    hot_android_issues_data: Optional[List[Dict[str, Any]]] = None,
    patent_trend_data: Optional[List[Dict[str, Any]]] = None,
    lang: str = "bilingual",
    output_path: Optional[str] = None,
) -> str:
    """Xuất toàn bộ dữ liệu RSS ra file JSON để lưu trữ hoặc chia sẻ.
    
    Hàm này thu thập tất cả thông tin cần thiết từ các bài báo và lưu vào JSON.
    Kết quả có thể được dùng lại bởi hàm `export_full_security_report_html_from_json`.
    
    Args:
        global_information_data: Dữ liệu section Global Information
        service: Tên service (ví dụ: "RSS")
        new_features_samsung_data: Dữ liệu section New Features Samsung
        new_features_iphone_data: Dữ liệu section New Features iPhone
        new_features_china_data: Dữ liệu section New Features China
        hot_android_issues_data: Dữ liệu section Hot Android Issues
        patent_trend_data: Dữ liệu section Patent Trend
        lang: Ngôn ngữ output ("vi", "en", "bilingual")
        output_path: Đường dẫn file output (optional, mặc định tạo tự động)
    
    Returns:
        Đường dẫn file JSON đã xuất
    """
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    # Fallback dữ liệu mặc định
    _nf_default = global_information_data
    new_features_samsung_data = new_features_samsung_data if new_features_samsung_data is not None else _nf_default
    new_features_iphone_data = new_features_iphone_data if new_features_iphone_data is not None else _nf_default
    new_features_china_data = new_features_china_data if new_features_china_data is not None else _nf_default
    hot_android_issues_data = hot_android_issues_data if hot_android_issues_data is not None else global_information_data
    patent_trend_data = patent_trend_data if patent_trend_data is not None else global_information_data
    
    # Xác định các trường cần thiết cho mỗi bài báo
    def extract_article_fields(item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "published": item.get("published", ""),
            "snippet": item.get("snippet", ""),
            "summary_vi": item.get("summary_vi", ""),
            "summary_en": item.get("summary_en", ""),
            "tags": item.get("tags", []),
            "image": item.get("image", ""),
        }
    
    # Tạo cấu trúc JSON
    report_data = {
        "metadata": {
            "service": service,
            "lang": lang,
            "timestamp": NOW,
            "duration": DURATION,
            "exported_at": TODAY,
        },
        "sections": {
            "global_information": [extract_article_fields(item) for item in global_information_data],
            "new_features_samsung": [extract_article_fields(item) for item in new_features_samsung_data],
            "new_features_iphone": [extract_article_fields(item) for item in new_features_iphone_data],
            "new_features_china": [extract_article_fields(item) for item in new_features_china_data],
            "hot_android_issues": [extract_article_fields(item) for item in hot_android_issues_data],
            "patent_trend": [extract_article_fields(item) for item in patent_trend_data],
        },
    }
    
    # Xác định đường dẫn file output
    if output_path is None:
        suffix = "BILINGUAL" if lang.lower() in {"bilingual", "both", "bi"} else ("EN" if lang.lower() == "en" else "VI")
        output_path = os.path.join(
            OUTPUT_PATH,
            f"results_{NOW}_{DURATION}days_{service}_FULL_REPORT_{suffix}.json",
        )
    
    # Ghi file JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"[EXPORT] Xuất JSON báo cáo RSS thành công ra {output_path}")
    return output_path


def export_full_security_report_html_from_json(
    json_file_path: str,
    lang: Optional[str] = None,
) -> str:
    """Đọc file JSON báo cáo RSS và xuất ra file HTML.
    
    Hàm này đọc dữ liệu từ file JSON đã được xuất bởi `export_rss_report_to_json`
    và gọi `export_full_security_report_html` để tạo file HTML.
    
    Args:
        json_file_path: Đường dẫn file JSON input
        lang: Ngôn ngữ output (optional, nếu None sẽ dùng lang từ metadata trong JSON)
    
    Returns:
        Đường dẫn file HTML đã xuất
    """
    # Đọc file JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    
    # Lấy metadata
    metadata = report_data.get("metadata", {})
    service = metadata.get("service", "RSS")
    output_lang = lang if lang else metadata.get("lang", "bilingual")
    
    # Lấy dữ liệu các sections
    sections = report_data.get("sections", {})
    global_information_data = sections.get("global_information", [])
    new_features_samsung_data = sections.get("new_features_samsung", [])
    new_features_iphone_data = sections.get("new_features_iphone", [])
    new_features_china_data = sections.get("new_features_china", [])
    hot_android_issues_data = sections.get("hot_android_issues", [])
    patent_trend_data = sections.get("patent_trend", [])
    
    logger.info(f"[EXPORT] Đọc JSON từ {json_file_path} để xuất HTML")
    
    # Gọi hàm xuất HTML
    return export_full_security_report_html(
        global_information_data=global_information_data,
        service=service,
        new_features_samsung_data=new_features_samsung_data,
        new_features_iphone_data=new_features_iphone_data,
        new_features_china_data=new_features_china_data,
        hot_android_issues_data=hot_android_issues_data,
        patent_trend_data=patent_trend_data,
        lang=output_lang,
    )
