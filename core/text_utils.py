"""文本工具函数"""
import re
from docx import Document
import io


def count_chinese(text: str) -> int:
    """统计中文字符数量"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def extract_hashtags(text: str) -> list[str]:
    """提取所有话题标签"""
    return re.findall(r'#[^\s#]+', text)


def count_tag_occurrences(text: str, tag: str) -> int:
    """计算特定标签在文本中的出现次数（支持 #标签 3 格式）"""
    pattern = re.escape(tag) + r'(?:\s+(\d+))?'
    matches = re.findall(pattern, text)
    if matches:
        for m in matches:
            if m and m.isdigit():
                return int(m)
        return len(matches)
    return 0


def extract_titles(text: str) -> list[str]:
    """从文本中提取标题行（非空、非标签、长度适中的行）"""
    lines = text.strip().split('\n')
    titles = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and 5 <= len(line) <= 50:
            titles.append(line)
    return titles


def split_content(text: str) -> dict:
    """将完整文本拆分为标题、正文、标签"""
    lines = text.strip().split('\n')
    titles = []
    body_lines = []
    tags_line = ""

    in_body = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_body:
                body_lines.append("")
            continue

        # 检测标签行
        if stripped.count('#') >= 3:
            tags_line = stripped
            continue

        # 检测标题（短行，在正文之前）
        if not in_body and 5 <= count_chinese(stripped) <= 30 and len(titles) < 5:
            titles.append(stripped)
        else:
            in_body = True
            body_lines.append(stripped)

    body = '\n'.join(body_lines).strip()
    return {"titles": titles, "body": body, "tags": tags_line}


def read_docx(file) -> str:
    """读取 .docx 文件内容"""
    doc = Document(io.BytesIO(file.read()))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return '\n'.join(paragraphs)
