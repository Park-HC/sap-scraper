def td_text_parser(td_data):
    if td_data.text and td_data.text.strip():
        td_text = td_data.text.strip()
        return td_text
    elif td_data.select('input'):
        return True if td_data.select('input')[0].get('checked') else False
    else:
        return None
