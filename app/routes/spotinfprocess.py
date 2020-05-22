import docx
def opens(url):
    dp = []
    val = r'{}'.format(url)
    open = docx.Document(val)
    for t in open.paragraphs:
        dp.append(t.text)
        # print(t.text)
    return dp




