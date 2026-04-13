Hiện tại tôi đang làm chương trình tự động xuất ra các bài báo hàng tuần liên quan đến Security có sự hỗ trợ tóm tắt của AI và tôi đang muốn xây dựng FE mới cho đẹp hơn bằng AI. Tôi sẽ gửi cho bạn file code liên quan đến phần sử dụng để xuất ra file html và thông tin mẫu về danh sách các bài báo để tổng hợp thành trang web để bạn hiểu rõ hơn nhé. Tôi cần bạn làm cho tôi 1 prompt thật chuyên nghiệp để xuất ra được 1 trang web tổng hợp các bài báo mới (sẽ có thêm 1 vài nội dung khác so với hiện tại).

Minh họa danh sách các bài báo đầu vào của tôi như sau:
[
    {
        "title": "Cracks in the Bedrock: Agent God Mode",
        "link": "https://unit42.paloaltonetworks.com/exploit-of-aws-agentcore-iam-god-mode/",
        "published": "2026-04-08T22:00:51+00:00",
        "snippet": "<p>Unit 42 reveals \"Agent God Mode\" in Amazon Bedrock AgentCore. Broad IAM permissions lead to privilege escalation and data exfiltration risks.</p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/exploit-of-aws-agentcore-iam-god-mode/\">Cracks in the Bedrock: Agent God Mode</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/03_Cloud_cybersecurity_research_Category_1505x922.jpg",
        "readtime": "8",
        "tags": [
            "Malware",
            "Threat Research",
            "agentcore",
            "AI agents",
            "AWS",
            "bedrock",
            "DNS tunneling",
            "exfiltration",
            "IAM",
            "identity",
            "killchain",
            "privilege escalation",
            "Sandbox"
        ],
        "content": "Cracks in the Bedrock: Agent God Mode\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Cen...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    },
    {
        "title": "Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox",
        "link": "https://unit42.paloaltonetworks.com/bypass-of-aws-sandbox-network-isolation-mode/",
        "published": "2026-04-07T22:00:11+00:00",
        "snippet": "<p>Unit 42 uncovers critical vulnerabilities in Amazon Bedrock AgentCore's sandbox, demonstrating DNS tunneling and credential exposure. </p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/bypass-of-aws-sandbox-network-isolation-mode/\">Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/05_Cloud_cybersecurity_research_Overview_1920x900.jpg",
        "readtime": "13",
        "tags": [
            "Malware",
            "Threat Research",
            "agentcore",
            "agentcore runtime",
            "AWS",
            "DNS tunneling",
            "GenAI",
            "Sandbox"
        ],
        "content": "Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Center...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    },
    {
        "title": "Understanding Current Threats to Kubernetes Environments",
        "link": "https://unit42.paloaltonetworks.com/modern-kubernetes-threats/",
        "published": "2026-04-06T22:00:08+00:00",
        "snippet": "<p>Unit 42 uncovers escalating Kubernetes attacks, detailing how threat actors exploit identities and critical vulnerabilities to compromise cloud environments.</p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/modern-kubernetes-threats/\">Understanding Current Threats to Kubernetes Environments</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/03_Malware_Category_1920x900-3.jpg",
        "readtime": "20",
        "tags": [
            "Malware",
            "Threat Research",
            "audit logs",
            "Cloud",
            "Containers",
            "Kubernetes",
            "PowerShell",
            "queries",
            "react server",
            "react2shell"
        ],
        "content": "Understanding Current Threats to Kubernetes Environments\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Center...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    }
]

Lưu ý là chỉ có 4 trường "title", "link", "published", "snippet" là chắc chắn có thông tin, còn các trường khác có thể là rỗng ("") trong trường hợp không có thông tin.

Prompt hiện tại tôi nghĩ ra: "Thiết kế trang web cho tôi, tôi muốn 1 trang web tổng hợp các bài báo, thông tin liên quan đến lĩnh vực Security mới nhất mỗi tuần, đặc biệt là Security liên quan đến smartphone. Tôi muốn trang web bao gồm 4 phần chính là: Global Information, New Features, Hot Android Issues, Security Patent Trend. Trong phần New Features có các mục con là Samsung, Iphone và Các hãng điện thoại Trung Quốc, trong mỗi mục sẽ có Overall thông tin và dưới là danh sách các bài báo mới nhất của từng hãng, dưới mỗi bài báo sẽ là phần tóm tắt nội dung chính bài báo do AI tóm tắt. Trong phần Hot Android Issues, Security Patent Trend thì sẽ có các thống kê và dưới danh sách các bài báo cùng với sự tóm tắt của AI. Trang web sẽ hỗ trợ 2 ngôn ngữ là tiếng Anh và tiếng Việt. Nếu có quá nhiều bài báo thì sẽ phân trang. Phong cách Tạp chí công nghệ hiện đại với các tông màu tươi với nền sáng và mang lại cảm giác thoải mái tiện nghi cho người đọc, tôi muốn mỗi bài báo được trình bày theo dải ngang. Tôi muốn mỗi phần trong 4 phần chính được hiển thị ở 1 Tab riêng."


Hãy làm cho tôi 1 prompt thật chuyên nghiệp để xuất ra được 1 trang web mới bằng Stick.

=================================================================================================
Design a modern, high-end "Cybersecurity Weekly News Aggregator" web dashboard with a bright, airy "Modern Tech Magazine" aesthetic. The interface should feel professional, comfortable for long-reading, and highly organized.
Layout & Navigation:


A clean Header with a Logo placeholder on the left and a Language Toggle (EN/VI) on the right.

Main Navigation using a Horizontal Tab System with 4 primary categories: [Global Information], [New Features], [Hot Android Issues], and [Security Patent Trend].
Section-Specific UI:


Global Information: A vertical list of news.

New Features: Inside this tab, include a secondary sub-navigation (pill-style) for [Samsung], [iPhone], and [Chinese Brands]. Each sub-section starts with a highlighted "Overall Trends" summary card, followed by the article list.

Hot Android Issues & Security Patent Trend: Include a "Quick Stats" section at the top (using mini-charts or data cards) before the article list.
Article Component (Horizontal Strip Design):


Layout each article as a horizontal row (strip).

Components per row: Title (bold, clickable), Metadata (Publication Date, Read Time - if available, Tags as small badges), Snippet (short description).

Feature an "AI Summary" box nested under each article with a soft background color to distinguish it.

Data Handling: Ensure a clean fallback if "image" or "readtime" is empty.
Visual Style:


Theme: Light mode, pure white background (#FFFFFF) with very soft gray borders.

Typography: Clean Sans-serif (Inter or Roboto). High contrast for readability.

Accents: Use a vibrant "Security Blue" or "Teal" for links and active states.

Interactivity: Smooth transitions between tabs. Add pagination controls (Previous/Next/Page Numbers) at the bottom.
Output: Responsive React/Tailwind CSS code that is clean and ready for dynamic JSON data injection.

Here's an illustration of my input article list:
[
    {
        "title": "Cracks in the Bedrock: Agent God Mode",
        "link": "https://unit42.paloaltonetworks.com/exploit-of-aws-agentcore-iam-god-mode/",
        "published": "2026-04-08T22:00:51+00:00",
        "snippet": "<p>Unit 42 reveals \"Agent God Mode\" in Amazon Bedrock AgentCore. Broad IAM permissions lead to privilege escalation and data exfiltration risks.</p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/exploit-of-aws-agentcore-iam-god-mode/\">Cracks in the Bedrock: Agent God Mode</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/03_Cloud_cybersecurity_research_Category_1505x922.jpg",
        "readtime": "8",
        "tags": [
            "Malware",
            "Threat Research",
            "agentcore",
            "AI agents",
            "AWS",
            "bedrock",
            "DNS tunneling",
            "exfiltration",
            "IAM",
            "identity",
            "killchain",
            "privilege escalation",
            "Sandbox"
        ],
        "content": "Cracks in the Bedrock: Agent God Mode\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Cen...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    },
    {
        "title": "Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox",
        "link": "https://unit42.paloaltonetworks.com/bypass-of-aws-sandbox-network-isolation-mode/",
        "published": "2026-04-07T22:00:11+00:00",
        "snippet": "<p>Unit 42 uncovers critical vulnerabilities in Amazon Bedrock AgentCore's sandbox, demonstrating DNS tunneling and credential exposure. </p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/bypass-of-aws-sandbox-network-isolation-mode/\">Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/05_Cloud_cybersecurity_research_Overview_1920x900.jpg",
        "readtime": "13",
        "tags": [
            "Malware",
            "Threat Research",
            "agentcore",
            "agentcore runtime",
            "AWS",
            "DNS tunneling",
            "GenAI",
            "Sandbox"
        ],
        "content": "Cracks in the Bedrock: Escaping the AWS AgentCore Sandbox\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Center...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    },
    {V
        "title": "Understanding Current Threats to Kubernetes Environments",
        "link": "https://unit42.paloaltonetworks.com/modern-kubernetes-threats/",
        "published": "2026-04-06T22:00:08+00:00",
        "snippet": "<p>Unit 42 uncovers escalating Kubernetes attacks, detailing how threat actors exploit identities and critical vulnerabilities to compromise cloud environments.</p>\n<p>The post <a href=\"https://unit42.paloaltonetworks.com/modern-kubernetes-threats/\">Understanding Current Threats to Kubernetes Environments</a> appeared first on <a href=\"https://unit42.paloaltonetworks.com\">Unit 42</a>.</p>",
        "image": "https://unit42.paloaltonetworks.com/wp-content/uploads/2026/04/03_Malware_Category_1920x900-3.jpg",
        "readtime": "20",
        "tags": [
            "Malware",
            "Threat Research",
            "audit logs",
            "Cloud",
            "Containers",
            "Kubernetes",
            "PowerShell",
            "queries",
            "react server",
            "react2shell"
        ],
        "content": "Understanding Current Threats to Kubernetes Environments\nMenu\nTools\nATOMs\nSecurity Consulting\nAbout Us\nUnder Attack?\nThreat Research Center...",
        "summary_vi": "Sample AI summary for content of an artical in Vietnamese.",
        "summary_en": "Sample AI summary for content of an artical in English."
    }
]