def get_data_from_response(res):
    # with open("out.html", "w", encoding="utf-8") as f:
    #     f.write(res)
    script_tags = re.findall(r'<script\b[^>]*>.*?</script>', res, re.DOTALL | re.IGNORECASE)
    print(f"Found {len(script_tags)} <script> tags.")

    last_script_tag_content = None
    if script_tags:
        print("\nContent of the last <script> tag saved\n")
        # with open("last_script_tag.html", "w", encoding="utf-8") as f:
        #     f.write(script_tags[-1] if script_tags else "")
        last_script_tag_content = script_tags[-1]
    else:
        print("No <script> tags found.")


    data_tag = last_script_tag_content[27:-10]
    # with open("data_tag_info.html", "w", encoding="utf-8") as f:
    #     f.write(data_tag if data_tag else "")
    
    json_with_escaped_quotes = data_tag[27:-5]


    json_string = json_with_escaped_quotes.replace('\\"', '"')
    # with open("json_string.json", "w", encoding="utf-8") as f:
    #     f.write(json_string if json_string else "")


    try:
        json_decoded = json.loads(json_string)
        with open("json_decoded.json", "w", encoding="utf-8") as f:
            json.dump(json_decoded, f, ensure_ascii=False, indent=2)
        print("JSON decoded and saved to json_decoded.json")
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
    
    return json_decoded