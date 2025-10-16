import os

projectTypeEmojis = {
    "methodical": "📚",
    "program-hardware": "⚙️",
    "program": "🖥️",
    "nir": "⚛️",
}

projectTagsEmojis = {
    "Оплачиваемый": "💰",
    "Стартап": "🚀",
    "От компании": "🏢",
    "Проект-ВКР": "🎓",
    "ТехноШоу": "🤖",
}

projectStatuses = {
    "readyForWork": "Готов к работе",
    "start": "Начало работы над проектом",
    "presentation": "Презентация проекта",
    "poster": "Постерная сессия проекта",
}

projectTypes = {
    "methodical": "Методический",
    "program-hardware": "Программно-аппаратный",
    "program": "Программный",
    "nir": "Научно-исследовательский",
}

def escape_markdown_v2(text):
    if not isinstance(text, str):
        return text
    escape_chars = r'_*[]()~`>#+-=|{}.!' # List of all special characters in MarkdownV2 that must be escaped
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def new_vacancy_message(vacancy):
    values = {
        "id": vacancy.get('id', 'ERR'),
        "role": vacancy.get('role', 'ERR'),
        "description": vacancy.get('description', 'ERR').strip(),
        "manager": vacancy.get('managerName', 'ERR'),
        "requiredSkills": '\n'.join(["• " + s for s in vacancy.get('requiredSkills', ['ERR'])]),
        "developedSkills": '\n'.join(["• " + s for s in vacancy.get('developedSkills', ['ERR'])]),
        "project": vacancy.get('projectName', 'ERR'),
        "pid": vacancy.get('projectId', 'ERR'),
        "projectType": projectTypeEmojis.get(vacancy.get('logoSrc', 'ERR').split('/')[-1].split('.')[0], ''),
        "projectTags": ' '.join([projectTagsEmojis.get(tag if isinstance(tag, str) else tag.get('value', ''), '') for tag in vacancy.get('projectOfficeTags', []) if (tag if isinstance(tag, str) else tag.get('value', '')) in projectTagsEmojis]), # TODO: refactor
    }

    if values["role"] and isinstance(values["role"], str) and values["role"][0].isalpha():
        values["role"] = values["role"][0].upper() + values["role"][1:]

    for k in values:
        values[k] = escape_markdown_v2(values[k])

    template_path = os.path.join(os.path.dirname(__file__), "messageTemplates", "newVacancyMessage.md")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    return template.format(**values)


def new_statistics_message(data):
    total_vacancies = data.get("count", 0)
    vacancies = data.get("vacancies", [])

    status_counts = {}
    for v in vacancies:
        status = v.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    type_counts = {}
    for v in vacancies:
        project_type = v.get("logoSrc", "unknown").split('/')[-1].split('.')[0]
        type_counts[project_type] = type_counts.get(project_type, 0) + 1

    template_path = os.path.join(os.path.dirname(__file__), "messageTemplates", "statisticsMessage.md")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    type_lines   = '\n'.join([f"• {projectTypes.get(pt, pt)}: {count}" for pt, count in type_counts.items()])
    status_lines = '\n'.join([f"• {projectStatuses[status]}: {count}" for status, count in status_counts.items()])

    values = {
        "total_vacancies": total_vacancies,
        "status_lines": status_lines,
        "type_lines": type_lines
    }

    return template.format(**values)

