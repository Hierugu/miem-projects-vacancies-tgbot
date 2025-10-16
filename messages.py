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

