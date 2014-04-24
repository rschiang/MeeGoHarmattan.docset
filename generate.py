#!/usr/bin/python
import re
from os import system

pattern = re.compile(r"\['([^']+)','([^']+)',")
tree_data = open('Contents/Resources/Documents/treedata.js', 'r').read()
indices = pattern.findall(tree_data)
output = open('indices.sql', 'w+')
translators = [
  (re.compile(r"QML (\S+) Element"), 'Element'), 
  (re.compile(r"(\S+) Namespace"), 'Namespace'),
  (re.compile(r"(\S+) QML Plugin"), 'Module'),
]
excluded_pages = [
  'qt4/index.html', 'qt4/qtcore.html', 'qt4/qtgui.html', 
  'qtmobility/qml-plugins.html', 
]

# Table specifications
output.write("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")
output.write("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);")

def write_entry(title, type, path):
  output.write("INSERT INTO searchIndex(name,type,path) VALUES ('{0}','{1}','{2}');\n".format(title, type, path))

for title, path in indices:
  type = 'Entry'
  if path.startswith('guide/'):
    type = 'Guide'	# Guides
  elif path.startswith('manpages/'):
    type = 'Command'	# Man Pages
  elif path.startswith('categories/'):
    type = 'Category'	# Category
  elif title[0] == 'Q' and ' ' not in title and 'qt' in path:
    type = 'Class'	# Qt class
  elif title[0] == 'G' and ' ' not in title and 'glib' in path:
    type = 'Class'      # Glib class
  elif title.startswith('Gst') and ' ' not in title:
    type = 'Class'      # Gstreamer class
  elif title.startswith('gl') and path.startswith('opengl') or title.startswith('egl') and path.startswith('egl/'):
    type = 'Function'	# Open GL C-style functions
  elif 'class' in path and ' ' not in title:
    type = 'Class'	# Platform SDK class
  elif 'struct' in path and ' ' not in title:
    type = 'Struct'	# Platform SDK struct
  elif path.endswith('/main.html') or path.endswith('/index.html'):
    type = 'Library'	# Platform Library overview
  elif 'example' in path or title.startswith('Index') or 'API Index' in title:
    continue	# Examples and indices page
  elif path in excluded_pages:
    continue

  # Translate long names
  for expr, alt_type in translators:
    match = expr.match(title)
    if match:
      title = match.group(1)
      type = alt_type
  
  write_entry(title, type, path)

output.close()

# Write indices to SQLite library
system('mkdir -p Contents/Resources/')
system('sqlite3 Contents/Resources/docSet.dsidx < indices.sql')
