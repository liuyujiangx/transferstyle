import docx
def opens():
    dp = []
    val = r'{}'.format()
    open = docx.Document(val)
    for t in open.paragraphs:
        dp.append(t.text)
        # print(t.text)
    return dp
opens()



