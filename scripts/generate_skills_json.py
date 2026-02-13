import os
import json
import re

skills_dir = os.path.join('.claude', 'skills')
out_path = os.path.join('skills', 'skills.json')

skills = []

for skill_folder in os.listdir(skills_dir):
    folder_path = os.path.join(skills_dir, skill_folder)
    skill_md = os.path.join(folder_path, 'SKILL.md')
    if os.path.isfile(skill_md):
        with open(skill_md, encoding='utf-8') as f:
            content = f.read()
        # Extract YAML frontmatter
        match = re.search(r'^---\s*([\s\S]+?)---', content, re.MULTILINE)
        meta = {}
        if match:
            for line in match.group(1).splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"')
        # Fallbacks
        skill_id = meta.get('name', skill_folder)
        name = meta.get('name', skill_folder.replace('-', ' ').title())
        description = meta.get('description', '')
        skills.append({
            'id': skill_id,
            'name': name,
            'plugin': '',
            'description': description,
            'inputs': []
        })

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(skills, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(skills)} skills to {out_path}")
