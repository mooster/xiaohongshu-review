"""硬性审核检查引擎"""
import re
from core.text_utils import count_chinese, extract_hashtags, count_tag_occurrences


def check_word_count(body: str, config: dict) -> dict:
    """字数审核"""
    cc = count_chinese(body)
    wc = config["word_count"]
    return {
        "id": "word_count",
        "name": "字数审核",
        "pass": wc["min"] <= cc <= wc["max"],
        "value": cc,
        "target": f"{wc['min']}-{wc['max']}",
        "message": f"{cc}字" if wc["min"] <= cc <= wc["max"] else (
            f"{cc}字，不足{wc['min']}字" if cc < wc["min"] else f"{cc}字，超过{wc['max']}字"
        ),
        "editable": False,
    }


def check_title_count(titles: list[str], config: dict) -> dict:
    """标题数量审核"""
    required = config["titles"]["required_count"]
    actual = len(titles)
    return {
        "id": "title_count",
        "name": "标题数量审核",
        "pass": actual == required,
        "value": actual,
        "target": required,
        "message": f"{actual}个标题" if actual == required else f"需要{required}个标题，当前{actual}个",
        "editable": False,
    }


def check_title_keywords(titles: list[str], config: dict) -> dict:
    """标题关键词审核"""
    keywords = config["titles"]["keywords"]
    all_titles = " ".join(titles)
    details = []
    for kw in keywords:
        found = kw in all_titles
        found_in = []
        if found:
            for i, t in enumerate(titles):
                if kw in t:
                    found_in.append(i + 1)
        details.append({
            "keyword": kw,
            "found": found,
            "found_in_titles": found_in,
        })
    all_pass = all(d["found"] for d in details)
    missing = [d["keyword"] for d in details if not d["found"]]
    return {
        "id": "title_keywords",
        "name": "标题关键词审核",
        "pass": all_pass,
        "details": details,
        "missing": missing,
        "message": "标题关键词齐全" if all_pass else f"标题缺少关键词：{'、'.join(missing)}",
        "editable": True,
        "suggestion": f"建议在标题中加入：{'、'.join(missing)}" if missing else "",
    }


def check_hashtags(tags_text: str, config: dict) -> dict:
    """话题标签审核"""
    required = config["hashtags"]["required"]
    details = []
    for req in required:
        tag = req["tag"]
        min_count = req["min_count"]
        actual = count_tag_occurrences(tags_text, tag)
        details.append({
            "tag": tag,
            "required_count": min_count,
            "actual_count": actual,
            "pass": actual >= min_count,
        })
    all_pass = all(d["pass"] for d in details)
    missing = [d["tag"] for d in details if not d["pass"]]
    return {
        "id": "hashtags",
        "name": "话题标签审核",
        "pass": all_pass,
        "details": details,
        "missing": missing,
        "message": "话题标签齐全" if all_pass else f"缺少标签：{'、'.join(missing)}",
        "editable": True,
        "suggestion": " ".join(missing) if missing else "",
    }


def check_forbidden_words(full_text: str, config: dict) -> dict:
    """违禁词审核"""
    forbidden_list = config["forbidden_words"]
    violations = []

    for fw in forbidden_list:
        word = fw["word"]
        exceptions = fw.get("exceptions", [])
        replacement = fw.get("replacement", "")
        category = fw.get("category", "禁止词")

        start = 0
        while True:
            idx = full_text.find(word, start)
            if idx == -1:
                break
            # 检查是否在例外中
            is_exception = False
            for exc in exceptions:
                exc_idx = full_text.find(exc, max(0, idx - len(exc)))
                if exc_idx != -1 and idx >= exc_idx and idx < exc_idx + len(exc):
                    is_exception = True
                    break
            if not is_exception:
                ctx_start = max(0, idx - 15)
                ctx_end = min(len(full_text), idx + len(word) + 15)
                violations.append({
                    "word": word,
                    "category": category,
                    "position": idx,
                    "context": full_text[ctx_start:ctx_end],
                    "replacement": replacement,
                })
            start = idx + 1

    # 特殊替换规则
    special_violations = []
    for rule in config.get("special_replacements", []):
        find_text = rule["find"]
        start = 0
        while True:
            idx = full_text.find(find_text, start)
            if idx == -1:
                break
            next_char = full_text[idx + len(find_text)] if idx + len(find_text) < len(full_text) else ""
            if next_char != "粉":
                ctx_start = max(0, idx - 10)
                ctx_end = min(len(full_text), idx + len(find_text) + 10)
                special_violations.append({
                    "find": find_text,
                    "context": full_text[ctx_start:ctx_end],
                    "replace_with": rule["replace_with"],
                    "description": rule.get("description", ""),
                })
            start = idx + 1

    # 标签中的违禁词检查
    tags = extract_hashtags(full_text)
    tag_violations = []
    safe_tags = set(config.get("safe_tags", ["#防敏奶粉", "#第一口奶粉"]))
    for tag in tags:
        for fw in forbidden_list:
            word = fw["word"]
            if word in tag and tag not in safe_tags:
                tag_violations.append({"tag": tag, "word": word})

    all_pass = len(violations) == 0 and len(special_violations) == 0 and len(tag_violations) == 0
    return {
        "id": "forbidden_words",
        "name": "违禁词审核",
        "pass": all_pass,
        "violations": violations,
        "special_violations": special_violations,
        "tag_violations": tag_violations,
        "message": "未发现违禁词" if all_pass else f"发现{len(violations)}处违禁词、{len(special_violations)}处特殊违规、{len(tag_violations)}处标签违规",
        "editable": True,
    }


def check_structure(body: str, config: dict) -> dict:
    """文章结构审核 - 检查内容是否包含4个主题且顺序正确（不要求严格分段）"""
    paragraphs_spec = config["structure"]["paragraphs"]

    # 在全文中搜索每个主题的锚点关键词位置
    detected = []
    for spec in paragraphs_spec:
        positions = []
        found_keywords = []
        for kw in spec["anchor_keywords"]:
            idx = body.find(kw)
            if idx != -1:
                positions.append(idx)
                found_keywords.append(kw)

        avg_pos = sum(positions) / len(positions) if positions else -1
        detected.append({
            "name": spec["name"],
            "found": len(positions) > 0,
            "found_keywords": found_keywords,
            "total_anchor": len(spec["anchor_keywords"]),
            "avg_position": avg_pos,
        })

    # 检查所有主题是否都有内容
    all_found = all(d["found"] for d in detected)
    missing_sections = [d["name"] for d in detected if not d["found"]]

    # 检查顺序（按锚点关键词的平均位置排序）
    found_topics = [d for d in detected if d["found"]]
    positions = [d["avg_position"] for d in found_topics]
    order_correct = all(positions[i] <= positions[i + 1] for i in range(len(positions) - 1))

    actual_order = [d["name"] for d in sorted(found_topics, key=lambda x: x["avg_position"])]
    expected_order = [p["name"] for p in paragraphs_spec]

    return {
        "id": "structure",
        "name": "文章结构审核",
        "pass": all_found and order_correct,
        "detected": detected,
        "expected_order": expected_order,
        "actual_order": actual_order,
        "missing_sections": missing_sections,
        "order_correct": order_correct,
        "message": "内容结构与顺序正确" if (all_found and order_correct) else (
            f"缺少内容：{'、'.join(missing_sections)}" if missing_sections else
            f"内容顺序不正确，当前：{'→'.join(actual_order)}"
        ),
        "editable": False,
    }


def check_selling_points(body: str, config: dict) -> dict:
    """卖点必提词审核"""
    paragraphs_spec = config["structure"]["paragraphs"]
    results = []
    total = 0
    passed = 0

    for para_spec in paragraphs_spec:
        para_results = {
            "paragraph_name": para_spec["name"],
            "selling_points": [],
        }
        for sp in para_spec["selling_points"]:
            if not sp["required_keywords"]:
                para_results["selling_points"].append({
                    "id": sp["id"],
                    "name": sp["name"],
                    "soft_only": True,
                    "pass": True,
                    "paraphrase_ref": sp.get("paraphrase_ref", ""),
                })
                continue

            total += 1
            kw_results = []
            for kw in sp["required_keywords"]:
                kw_results.append({"keyword": kw, "found": kw in body})

            sp_pass = all(r["found"] for r in kw_results)
            if sp_pass:
                passed += 1

            missing = [r["keyword"] for r in kw_results if not r["found"]]
            para_results["selling_points"].append({
                "id": sp["id"],
                "name": sp["name"],
                "soft_only": False,
                "pass": sp_pass,
                "keywords": kw_results,
                "missing": missing,
                "paraphrase_ref": sp.get("paraphrase_ref", ""),
            })
        results.append(para_results)

    return {
        "id": "selling_points",
        "name": "卖点必提词审核",
        "pass": passed == total,
        "total": total,
        "passed": passed,
        "paragraphs": results,
        "message": f"卖点必提词 {passed}/{total} 通过" if passed == total else f"卖点必提词 {passed}/{total} 通过，{total - passed}个卖点有缺失",
        "editable": True,
    }


def run_all_checks(titles: list[str], body: str, tags: str, config: dict) -> list[dict]:
    """运行所有硬性审核"""
    full_text = "\n".join(titles) + "\n" + body + "\n" + tags
    hr = config["hard_rules"]

    return [
        check_word_count(body, hr),
        check_title_count(titles, hr),
        check_title_keywords(titles, hr),
        check_hashtags(tags, hr),
        check_forbidden_words(full_text, hr),
        check_structure(body, hr),
        check_selling_points(body, hr),
    ]
