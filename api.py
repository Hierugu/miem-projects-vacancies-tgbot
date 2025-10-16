import urllib.parse
import sys
import re
import json
import random
import string
import urllib.request
import urllib.error


def generate_boundary() -> str:
    return "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def encode_multipart_formdata(fields: dict, boundary: str) -> bytes:
    lines = []
    for key, value in fields.items():
        lines.append(f'--{boundary}')
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        lines.append(f'Content-Disposition: form-data; name="{key}"')
        lines.append('')
        lines.append(str(value))
    lines.append(f'--{boundary}--')
    lines.append('')
    body = '\r\n'.join(lines)
    return body.encode('utf-8')

def send_request(url: str, form_data: dict, headers: dict = None, timeout: int = 20, request_type: str = "POST") -> str:
    boundary = generate_boundary()
    encoded_data = encode_multipart_formdata(form_data, boundary)

    default_headers = {
        "Content-Length": str(len(encoded_data)),
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        
    }
    if headers:
        default_headers.update(headers)
    req = urllib.request.Request(url, data=encoded_data, method=request_type.upper(), headers=default_headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get_content_charset()
            encoding = content_type or "utf-8"
            data = resp.read()
            return data.decode(encoding, errors="replace")
    except urllib.error.HTTPError as e:
        return f"HTTP Error: {e.code} {e.reason}\n" + e.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"Request failed: {e}"

def extract_json(res):
    payloads = res.split('\n')
    vacancies_payload = payloads[1]
    json_string = vacancies_payload[vacancies_payload.index('{'):vacancies_payload.rindex('}')+1]
    json_object = json.loads(json_string)
    return json_object

def call_get_vacancies_api(offset=0, limit=20, headers=None):
    url = "https://cabinet.miem.hse.ru/vacancies"
    headers = {
        "Next-Action": "602d4483bc1bb1d43a416671458cf4fb9ac90c054b"
    }
    form_data = {
        "1": {"id":"7f6a73e30041903a4ef9e45b5ead20a7c8325eeddf","bound": None},
        "0": ["$F1",{"query":{"offset":offset,"limit":limit, "search":"$undefined","projectTypeId":"$undefined","industryId":"$undefined","projectStatuses":"$undefined","projectOfficeTagIds":"$undefined","controlPoints":"$undefined"}}]
    }

    res = send_request(url, form_data, headers=headers)
    json_data = extract_json(res)
    return json_data

def save_vacancy_ids(vacancies, filename="vacancy_ids.txt"):
    """Save all vacancy IDs from a list of dicts to a file, one per line."""
    with open(filename, "w", encoding="utf-8") as f:
        for v in vacancies:
            vid = v.get("id")
            if vid is not None:
                f.write(str(vid) + "\n")

if __name__ == '__main__':
    json_data = call_get_vacancies_api(offset=0, limit=10000)
    vacancies_total_count, vacancies = json_data.get("count", -1), json_data.get("vacancies", [])

    if vacancies_total_count != len(vacancies):
        print("Error: count mismatch")
        print(f"Total vacancies: {vacancies_total_count}")
        print(f"Vacancies in list: {len(vacancies)}")
        sys.exit(1)

    # Save all vacancy IDs to file
    save_vacancy_ids(vacancies)
    print(f"Saved {len(vacancies)} vacancy IDs to vacancy_ids.txt")

    # for v in vacancies:
    #     print(f"{v.get('id')} {v.get('role')}")
    for k, v in vacancies[0].items():
        print(f"{k}:           {type(v)} {v}")
    
    print(f"Total vacancies: {len(vacancies)}")

    statuses = set(v.get("status") for v in vacancies if "status" in v)
    print("Different status values:", statuses)





