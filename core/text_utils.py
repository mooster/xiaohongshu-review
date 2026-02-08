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


def read_docx(file) -> str:
    """读取 .docx 文件内容"""
    doc = Document(io.BytesIO(file.read()))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return '\n'.join(paragraphs)
