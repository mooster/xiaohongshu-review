"""自动修复引擎 - 一键修复所有可自动修复的问题"""
import re
import difflib
from core.text_utils import count_chinese


def auto_fix_all(titles, body, tags, config):
    """自动修复所有违禁词和特殊替换，返回修复后的内容和变更记录"""
    hr = config["hard_rules"]
    changes = []

    new_titles = list(titles)
    new_body = body
    new_tags = tags

    # 1. 修复违禁词
    for fw in hr["forbidden_words"]:
        word = fw["word"]
        replacement = fw.get("replacement", "")
        exceptions = fw.get("exceptions", [])

        if not replacement:
            continue  # 没有替换建议的跳过自动修复

        # 在正文中替换
        for text_type, text in [("正文", new_body), ("标签", new_tags)]:
            count = 0
            result = ""
            i = 0
            while i < len(text):
                idx = text.find(word, i)
                if idx == -1:
                    result += text[i:]
                    break
                # 检查例外
                is_exc = False
                for exc in exceptions:
                    exc_idx = text.find(exc, max(0, idx - len(exc)))
                    if exc_idx != -1 and idx >= exc_idx and idx < exc_idx + len(exc):
                        is_exc = True
                        break
                if is_exc:
                    result += text[i:idx + len(word)]
                    i = idx + len(word)
                else:
                    result += text[i:idx] + replacement
                    count += 1
                    i = idx + len(word)

            if count > 0:
                if text_type == "正文":
                    new_body = result
                else:
                    new_tags = result
                changes.append({
                    "type": "违禁词",
                    "old": word,
                    "new": replacement,
                    "count": count,
                    "scope": text_type,
                })

        # 在标题中替换
        for ti in range(len(new_titles)):
            t = new_titles[ti]
            if word in t:
                is_exc = any(exc in t and t.find(word) >= t.find(exc) and t.find(word) < t.find(exc) + len(exc) for exc in exceptions if exc in t)
                if not is_exc:
                    new_titles[ti] = t.replace(word, replacement)
                    changes.append({
                        "type": "违禁词",
                        "old": word,
                        "new": replacement,
                        "count": t.count(word),
                        "scope": f"标题{ti+1}",
                    })

    # 2. 特殊替换（通用逻辑）
    for rule in hr.get("special_replacements", []):
        find = rule["find"]
        replace = rule["replace_with"][-1]  # 用最后一个选项
        skip_suffix = rule.get("skip_if_followed_by", "")

        for text_type, text in [("正文", new_body)]:
            count = 0
            result = ""
            i = 0
            while i < len(text):
                idx = text.find(find, i)
                if idx == -1:
                    result += text[i:]
                    break
                # 跳过条件：后面紧跟指定字符（如"粉"）
                skip = False
                if skip_suffix:
                    next_pos = idx + len(find)
                    if next_pos < len(text) and text[next_pos:next_pos + len(skip_suffix)] == skip_suffix:
                        skip = True
                # 跳过条件：已经是完整替换词的一部分
                if not skip and replace in text[max(0, idx - len(replace)):idx + len(find) + len(replace)]:
                    skip = True

                if skip:
                    result += text[i:idx + len(find)]
                    i = idx + len(find)
                else:
                    result += text[i:idx] + replace
                    count += 1
                    i = idx + len(find)

            if count > 0:
                new_body = result
                changes.append({
                    "type": "特殊替换",
                    "old": find,
                    "new": replace,
                    "count": count,
                    "scope": text_type,
                })

    # 3. 修复标签中的违禁标签
    problem_tags = {"#新生儿奶粉": None, "#防敏感奶粉": "#防敏奶粉"}
    for bad_tag, good_tag in problem_tags.items():
        if bad_tag in new_tags:
            if good_tag:
                new_tags = new_tags.replace(bad_tag, good_tag)
                changes.append({"type": "标签修复", "old": bad_tag, "new": good_tag, "count": 1, "scope": "标签"})
            else:
                new_tags = new_tags.replace(bad_tag, "")
                changes.append({"type": "标签删除", "old": bad_tag, "new": "(删除)", "count": 1, "scope": "标签"})

    # 4. 补齐缺失标签
    required_tags = hr["hashtags"]["required"]
    for req in required_tags:
        tag = req["tag"]
        if tag not in new_tags:
            sep = " " if new_tags and not new_tags.endswith(" ") else ""
            new_tags = new_tags.rstrip() + sep + tag
            changes.append({"type": "标签补齐", "old": "(缺失)", "new": tag, "count": 1, "scope": "标签"})

    return new_titles, new_body, new_tags, changes


def diff_highlight(text_before, text_after):
    """对比两段文本，返回带红绿黄高亮的 HTML (before_html, after_html)

    - 红色(hl-bad)：被删除的文字
    - 黄色(hl-change)：被替换的原文
    - 绿色(hl-good)：新增/替换后的文字
    """
    sm = difflib.SequenceMatcher(None, text_before, text_after, autojunk=False)
    before_parts = []
    after_parts = []

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            before_parts.append(text_before[i1:i2])
            after_parts.append(text_after[j1:j2])
        elif op == 'delete':
            before_parts.append(f'<span class="hl-bad">{text_before[i1:i2]}</span>')
        elif op == 'insert':
            after_parts.append(f'<span class="hl-good">{text_after[j1:j2]}</span>')
        elif op == 'replace':
            before_parts.append(f'<span class="hl-change">{text_before[i1:i2]}</span>')
            after_parts.append(f'<span class="hl-good">{text_after[j1:j2]}</span>')

    before_html = ''.join(before_parts).replace('\n', '<br>')
    after_html = ''.join(after_parts).replace('\n', '<br>')
    return before_html, after_html


def highlight_original(text, changes):
    """在原文中标红问题处"""
    result = text
    done = set()
    for c in changes:
        old = c["old"]
        if old in ("(缺失)", "(删除)") or old in done:
            continue
        if old in result:
            result = result.replace(old, f'<span class="hl-bad">{old}</span>')
            done.add(old)
    return result


def highlight_revised(text, changes):
    """在修改稿中标绿修改处，括号注明原文"""
    result = text
    # 按替换词长度降序，避免短词先替换导致长词匹配不到
    sorted_changes = sorted(changes, key=lambda c: len(c.get("new", "")), reverse=True)
    done = set()
    for c in sorted_changes:
        new = c["new"]
        old = c["old"]
        if new in ("(删除)",) or new in done:
            continue
        if old in ("(缺失)",):
            continue
        if new in result:
            result = result.replace(
                new,
                f'<span class="hl-good">{new}</span><span class="hl-note">←{old}</span>',
            )
            done.add(new)
    return result
