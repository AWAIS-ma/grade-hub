import re
import json

def normalize_header(h):
    if not h:
        return h
    return h.strip().lower().replace(' ', '_')

def clean_and_validate_rows(raw_rows):
    """
    Take raw extracted rows (list of dicts) and normalize keys to common set:
    Name, Roll No, Marks, Grade, Course
    """
    cleaned = []
    for r in raw_rows:
        row = {}
        # unify keys by simple mapping heuristics
        for k, v in r.items():
            if not k:
                continue
            key = k.strip().lower()
            val = v.strip() if isinstance(v, str) else v
            if 'name' in key:
                row['Name'] = val
            elif 'roll' in key or 'reg' in key:
                row['Roll No'] = val
            elif 'mark' in key or 'score' in key:
                row['Marks'] = val
            elif 'grade' in key:
                row['Grade'] = val
            elif 'course' in key or 'subject' in key:
                row['Course'] = val
            else:
                # keep extras
                row[k] = val
        # basic validations
        if not row.get('Roll No') and row.get('Name'):
            # try to parse roll no from a combined field
            possible = re.search(r'(\d{3,10})', ' '.join(str(x) for x in r.values()))
            if possible:
                row['Roll No'] = possible.group(1)
        cleaned.append(row)
    return cleaned
