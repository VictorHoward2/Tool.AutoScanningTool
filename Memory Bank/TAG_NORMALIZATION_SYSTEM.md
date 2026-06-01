# Hệ Thống Chuẩn Hóa Tags - 30 Canonical Tags

## Tổng Quan

Hệ thống này được thiết kế để giải quyết vấn đề tags không đồng nhất khi tổng hợp bài báo security từ nhiều nguồn. Thay vì để AI tự do tạo tags, chúng ta giới hạn trong **30 canonical tags** được định nghĩa trước.

## Vấn Đề Giải Quyết

**Trước đây:**
- Mỗi bài báo có tags hoàn toàn khác nhau
- AI tạo ra hàng trăm tags khác nhau cho cùng một khái niệm
- Khó filter, search và group articles
- Tags quá chi tiết (VD: "Galaxy S26", "CVE-2026-20182")

**Giải pháp:**
- 30 canonical tags cố định
- AI chỉ được chọn từ list này
- Tags đồng nhất across tất cả articles
- Dễ dàng filter và analytics

---

## 30 Canonical Tags

### 🔌 Device Tags (7 tags) - **Chọn ĐÚNG 1**

| Tag | Mô tả | Ví dụ áp dụng |
|-----|-------|---------------|
| Smartphone | Điện thoại (bao gồm foldable) | iPhone, Samsung Galaxy, Pixel, Xiaomi |
| Computer | PC, laptop, desktop, workstation | MacBook, Dell XPS, ThinkPad, iMac |
| Server & Cloud | Servers, cloud, data centers | AWS, Azure, Google Cloud, enterprise servers |
| IoT Device | Smart home, connected devices, automotive | Smart speakers, cameras, connected cars, routers |
| Wearable | Smartwatches, fitness trackers, AR/VR | Apple Watch, Galaxy Watch, Fitbit, Quest |
| Multiple Devices | Article covers 2+ device categories | Cross-platform attacks, multi-device trends |
| Non-categorized Devices | Peripherals, accessories | Non-categorized devices, peripherals, accessories |

### ⚠️ Threat Type Tags (8 tags) - **Chọn tối đa 2**

| Tag | Mô tả | Ví dụ áp dụng |
|-----|-------|---------------|
| Malware | Virus, trojan, spyware, mobile malware | Generic malware, trojans, spyware |
| Ransomware | Ransomware attacks | LockBit, Conti, Clop, ransomware gangs |
| Phishing | Phishing, social engineering | Email phishing, smishing, vishing |
| Data Breach | Data leaks, credential theft | Database leaks, password dumps |
| Zero-Day Exploit | Unpatched vulnerabilities | CVE chưa được fix, 0-day exploits |
| APT Attack | Advanced persistent threats | Nation-state attacks, state-sponsored |
| Network Attack | DDoS, MITM, web attacks | DDoS, man-in-the-middle, web exploits |
| Supply Chain Attack | Software supply chain attacks | Compromised updates, third-party breaches |

### 📋 Topic Tags (8 tags) - **Chọn tối đa 2**

| Tag | Mô tả | Ví dụ áp dụng |
|-----|-------|---------------|
| Vulnerability | CVE disclosures, security flaws | CVE announcements, bug disclosures |
| Security Update | Patches, updates, patch management | Patch Tuesday, software updates |
| Privacy Concern | Data collection, tracking, privacy | GDPR violations, data tracking |
| Cybercrime | Hacker arrests, cyber gangs, fraud | Cybercriminal arrests, fraud rings |
| Security Research | New findings, threat intelligence | Academic research, threat reports |
| Policy & Regulation | Laws, compliance, GDPR | Cybersecurity laws, regulations |
| AI | AI vulnerabilities, deepfakes, AI threats | AI exploits, deepfake detection |
| Cloud Security | Cloud breaches, misconfigurations | S3 bucket leaks, cloud IAM issues |

### 🏢 Brand Tags (9 tags) - **Chọn tối đa 2**

| Tag | Mô tả | Ví dụ áp dụng |
|-----|-------|---------------|
| Samsung | Samsung products only | Galaxy phones, Knox, Samsung apps |
| Apple | iPhone, iPad, Mac, iOS, Apple Watch | Apple ecosystem news |
| Google | Pixel, Google services | Pixel phones, Google Workspace |
| Microsoft | Windows, Surface, Azure, Office | Microsoft ecosystem |
| Android | General Android (non-brand specific) | AOSP, Android updates (stock) |
| iOS | iOS-specific news | iOS updates, iOS vulnerabilities |
| Windows | Windows-specific news | Windows updates, Windows exploits |
| China Brand | Huawei, Xiaomi, OPPO, Vivo, Honor | All Chinese brands |
| Github | Github-specific news | Github security issues, platform news |

---

## Quy Tắc Sử Dụng

### Tag Limits
```
Maximum 6 tags total per article:
- Exactly 1 Device tag (mandatory)
- Up to 2 Threat Type tags
- Up to 2 Topic tags  
- Up to 2 Brand tags
```

### Evidence Priority
```
1. Title (highest priority)
2. ai_summary_en
3. Snippet
4. tags_raw (hints only - ignore if not supported)
```

### Brand Tagging Rules
```
- Samsung: ONLY when 'Samsung' or Samsung product (Galaxy, Knox, One UI, Bixby) is mentioned
- Apple: ONLY for iPhone, iPad, Mac, iOS, macOS, Apple Watch, AirPods
- Google: ONLY for Google products (Pixel, Chrome, Gmail, Google Cloud, Android - stock)
- Microsoft: ONLY for Windows, Surface, Azure, Office 365, Microsoft 365, Edge
- Android: ONLY for general/stock Android issues, NOT Samsung/Huawei/Xiaomi specific
- iOS: ONLY for iOS-specific features/issues (not general mobile security)
- Windows: ONLY for Windows-specific news (not general PC security)
- China Brand: ONLY for Huawei, Xiaomi, OPPO, Vivo, Honor, OnePlus, Realme
- Github: ONLY for Github-specific news, security issues on Github platform
⚠️ If brand is not explicitly mentioned, DO NOT assign brand tag.
```

### Tag Order (Output)
```
Device → Threat Type → Topic → Brand
```

### Evidence Requirement - MOST IMPORTANT
```
BEFORE assigning ANY tag, you MUST find at least ONE specific keyword or phrase in the article content.
- If you cannot find evidence for a tag, DO NOT assign that tag.
- It is BETTER to have FEWER tags than WRONG tags.
- Ask yourself: 'What exact word/phrase in the article supports this tag?'
- If the answer is unclear or requires assumption, SKIP that tag.
```

### Confidence Check
```
For each tag you plan to assign, verify:
✓ Can I point to a specific word/phrase supporting this tag?
✓ Is this tag directly related to the MAIN topic (not just mentioned in passing)?
✓ Would another person agree this tag is appropriate based on the evidence?
If any answer is 'no' or 'unsure', SKIP that tag.
```

### When NOT to Tag (Examples)
```
- 'Security' mentioned generally → Do NOT add 'Vulnerability' without specific CVE/flaw
- 'Hack' mentioned without details → Do NOT add 'Malware' or 'Data Breach'
- 'Update' without security context → Do NOT add 'Security Update'
- 'China' mentioned → Do NOT add 'China Brand' without specific brand name
- 'Cloud' mentioned → Do NOT add 'Cloud Security' without security context
- 'AI' mentioned → Do NOT add 'AI' tag unless AI is central to security topic
- Article about 'smartphone security' → Do NOT add both 'Malware' and 'Phishing' without evidence of both
```

---

## Implementation Files

### `config/ai_prompts.py`
```python
# 30 canonical tags definitions
TAG_DEVICE_CANONICAL = (...)  # 7 tags
TAG_THREAT_CANONICAL = (...)  # 8 tags
TAG_TOPIC_CANONICAL = (...)   # 8 tags
TAG_BRAND_CANONICAL = (...)   # 9 tags

ALL_CANONICAL_TAGS = TAG_DEVICE_CANONICAL + TAG_THREAT_CANONICAL + TAG_TOPIC_CANONICAL + TAG_BRAND_CANONICAL
TAG_CANONICAL_SET = set(ALL_CANONICAL_TAGS)

# Prompt functions
normalize_tags_system()  # System prompt (enhanced with strict evidence rules)
normalize_tags_user()    # User prompt
validate_normalized_tags()  # Validation function
normalize_tags_output()  # Output normalization
```

### `core/ai_processor.py`
```python
_finalize_normalized_tags()  # Updated to use canonical tags
```

---

## API Usage

### Validate Tags
```python
from config.ai_prompts import validate_normalized_tags, TAG_CANONICAL_SET

is_valid, valid_tags, invalid_tags = validate_normalized_tags(["Phishing", "Smartphone", "FakeTag"])
# is_valid: False
# valid_tags: ["Phishing", "Smartphone"]
# invalid_tags: ["FakeTag"]
```

### Normalize Output
```python
from config.ai_prompts import normalize_tags_output

normalized, warnings = normalize_tags_output(
    tags=["phishing", "Smartphone", "Data Breach"],
    max_tags=6,
    ensure_device_tag=True
)
```

---

## Migration Guide

### Từ System Cũ Sang Mới

| Old Tags (50) | New Canonical Tag (30) |
|---------------|------------------------|
| Foldable Phone | Smartphone (merged) |
| Smart Home | IoT Device (merged) |
| Network Equipment | IoT Device (merged) |
| Automotive | IoT Device (merged) |
| Social Engineering | Phishing (merged) |
| Credential Theft | Data Breach (merged) |
| Web Attack | Network Attack (merged) |
| Mobile Attack | Malware (merged) |
| Security Patch | Security Update (merged) |
| Consumer Security | (removed - too generic) |
| Mobile Security | (removed - covered by Smartphone) |
| Enterprise Security | (removed - too generic) |
| Incident Response | (removed - niche) |
| Threat Intelligence | Security Research (merged) |
| Patch Management | Security Update (merged) |
| Huawei, Xiaomi, OPPO/OnePlus | China Brand (merged) |
| Linux | (removed - niche for our focus) |
| Geopolitical Threat | APT Attack (merged) |

---

## Monitoring & Maintenance

### Track These Metrics
1. **Tag Distribution**: Which tags are used most/least?
2. **Invalid Tags**: How often does AI create non-canonical tags?
3. **Missing Device Tag**: How often is device tag missing?
4. **User Feedback**: Are users finding what they need?

### Monthly Review Checklist
- [ ] Review unused tags (consider removing)
- [ ] Review frequently created non-canonical tags (consider adding)
- [ ] Check tag distribution for imbalances
- [ ] Update documentation if needed

---

## Future Enhancements

### Potential Additions (if needed)
- **Regional Tags**: APAC, EMEA, North America
- **Industry Tags**: Finance, Healthcare, Government
- **Severity Tags**: Critical, High, Medium, Low

### Deprecation Policy
- Tags unused for 3+ months → Candidate for removal
- New tags require ≥5% usage to be retained

---

## Contact

For questions or suggestions about the tag system, contact the development team.

**Version:** 2.1  
**Last Updated:** 2026-05-25  
**Changes:** Enhanced evidence requirements, added confidence check rules, strict brand tagging guidelines
**Author:** Cline SR
