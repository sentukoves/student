import lxml.html

file = open('txt' , encoding='utf-8')
open = lxml.html.document_fromstring(file.read())
err  = open.xpath('.//table[@summary = "Список призов"')
