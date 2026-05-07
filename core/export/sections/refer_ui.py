import os
import re

from config.settings import DURATION, NOW, OUTPUT_PATH


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def load_refer_template(template_rel_path: str) -> str:
    template_path = os.path.join(_project_root(), "export", "refer", template_rel_path)
    with open(template_path, "r", encoding="utf-8") as file:
        return file.read()


def build_output_path(service: str, section_key: str, lang_suffix: str) -> str:
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    filename = f"results_{NOW}_{DURATION}days_{service}_{section_key}_{lang_suffix}.html"
    return os.path.join(OUTPUT_PATH, filename)


def replace_section_after_marker(html: str, marker: str, new_section_html: str) -> str:
    marker_index = html.find(marker)
    if marker_index < 0:
        return html

    section_start = html.find("<section", marker_index)
    if section_start < 0:
        return html

    tag_pattern = re.compile(r"</?section\b", re.IGNORECASE)
    depth = 0
    section_end = -1
    for match in tag_pattern.finditer(html, section_start):
        token = match.group(0).lower()
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                section_end = html.find(">", match.start())
                if section_end >= 0:
                    section_end += 1
                break
        else:
            depth += 1

    if section_end < 0:
        return html
    return html[:section_start] + new_section_html + html[section_end:]


def safe_replace(html: str, old: str, new: str) -> str:
    return html.replace(old, new)
