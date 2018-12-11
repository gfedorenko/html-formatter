import html_formatter

params = html_formatter.read_params("params.txt")
print(params)
tags = html_formatter.analyze('ex.html')
print(tags)
