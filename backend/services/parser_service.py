def extract_text(file):
    content = file.file.read()
    return content.decode(errors="ignore")