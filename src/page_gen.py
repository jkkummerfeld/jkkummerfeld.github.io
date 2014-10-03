#!/usr/bin/env python

import glob, os
import pub_gen

def get_tab_depth(line):
  depth = 0
  for letter in line:
    if letter == '\t':
      depth += 1
    else:
      break
  return depth

def gen_menu(depth, page_names, url_base):
  tab = '\t' * depth
  ans = ''
  for name in page_names[::-1]:
    label = name
    if '|' in name:
      label = name.split('|')[1]
      name = name.split('|')[0]
    info = {'location': name + '.html', 'name': label, 'url_base': url_base}
    ans += tab + '<ul class="menu_links">\n'
    ans += tab + '\t' + ('<li class="menu_links"><a href="%(url_base)s%(location)s">%(name)s</a></li>\n' % info)
    ans += tab + '</ul>\n'
  return ans

def gen_software(source, indent, config, page_name, url_base, target_dir, pub_info):
  software = []
  cur = {}
  end = ''
  in_end = False
  for line in source:
    line = line.strip()
    if len(line) == 0:
      continue
    elif line == 'RAW:':
      in_end = True
    elif in_end:
      end += indent + line + '\n'
    elif line == '{':
      cur = {}
    elif line == '}':
      software.append(cur)
    else:
      field = line.split(' = ')[0]
      value = ' = '.join(line.split(' = ')[1:])
      cur[field] = value
  
  page = ''
  for system in software:
    page += indent + '<p>\n'
    page += indent + '\t<a href="%(url)s">%(name)s</a>\n' % system
    page += indent + '<br />\n'
    page += indent + '\t%(description)s\n' % system
    page += indent + '<br />\n'
    cite = pub_gen.replace_pub_ref(system['paper'], config, page_name, url_base, target_dir, pub_info)
    for part in cite:
      page += indent + part + '\n'
    page += indent + '</p>\n'
    page += indent + '<br />\n'
  page += end
  return page

def gen_page(page_template, page_content, config, page_name, url_base, target_dir, pub_info):
  page = ''
  for line in page_template:
    if line != '' and line[-1] == '\n':
      line = line[:-1]
    # nothing to insert
    if '%' not in line:
      page += line + '\n'
    # page name
    if '%(page_name)s' in line:
      page += (line % {'page_name': page_name}) + '\n'
    if '%(menu)s' in line:
      depth = get_tab_depth(line)
      page += gen_menu(depth, config['page_order'], url_base)
    if '%(content)s' in line:
      depth = get_tab_depth(line)
      tab = '\t' * depth
      if 'software' in page_name:
        page += gen_software(page_content, tab, config, page_name, url_base, target_dir, pub_info)
      else:
        for line in page_content:
          if line != '' and line[-1] =='\n':
            line = line[:-1]
          if '%(pub' in line:
            replacement = pub_gen.replace_pub_ref(line, config, page_name, url_base, target_dir, pub_info)
            for part in replacement:
              page += tab + part + '\n'
          else:
            page += tab + line + '\n'

  # Print the page to the target directory
  out = open(config['target_dir'] + '/' + page_name, 'w')
  print >> out, page
  out.close()

