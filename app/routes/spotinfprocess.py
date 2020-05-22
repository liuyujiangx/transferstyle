import docx
def opens():
    dp = []
    val = r'{}'.format('C:\\Users\\19145\\Desktop\\学习\\实训\\风格迁移\\景点.docx')
    open = docx.Document(val)
    for t in open.paragraphs:
        dp.append(t.text)
        # print(t.text)
    return dp
opens()



