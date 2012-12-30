import re

def remove_html_tags(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data) 

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
	"""Produce entities within text."""
	return "".join(html_escape_table.get(c,c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&#61;", "=")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
	
def extract(data, start, end):
	try:
		gdata = data.split(start)
		data = gdata[1].split(end)
		return data[0]
	except:
		return ''