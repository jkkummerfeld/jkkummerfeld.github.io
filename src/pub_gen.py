#!/usr/bin/env python

import glob

def gen_html(pub, target_dir):
	fields = {
		'author': '',
		'title': '',
		'date': '',
		'venue': '',
		'bib': '',
		'extra': ['No citations for this paper yet - be the first! Click the bib button and copy and paste it into your next paper :-)'],
		'num': pub['num'],
		'label': pub['label']
	}

	# author
	if 'author' in pub:
		fields['author'] = pub['author']
		author_list = pub['author'].split(' and ')
		if len(author_list) > 2:
			fields['author'] = ', '.join(author_list[:-1]) + ' and ' + author_list[-1]
	# title
	if 'title' in pub:
		fields['title'] = pub['title']
	# venue
	for option in ['booktitle', 'journal', 'school', 'institution']:
		if option in pub:
			fields['venue'] = pub[option]
			break
	# year
	if 'year' in pub:
		if 'month' in pub:
			fields['date'] = pub['month'] + " "
		fields['date'] += pub['year']
	# location
	if 'address' in pub:
		fields['location'] = pub['address']
	# pages
	if 'pages' in pub:
		fields['pages'] = '&ndash;'.join(pub['pages'].split('--'))
	# software
	if 'software' in pub:
		fields['software'] = pub['software']
	# citations
	if len(pub['citing_pubs']) > 0:
		extra_text = ['<p>Citations:</p>']
		pre_sort = []
		for label in pub['citing_pubs']:
			cite = pub['citing_pubs'][label]
			title = cite['title']
			author = cite['author']
			author_list = author.split(' and ')
			if len(author_list) > 2:
				author = ', '.join(author_list[:-1]) + ' and ' + author_list[-1]
			venue = ''
			for option in ['booktitle', 'journal', 'school', 'institution']:
				if option in cite:
					venue = cite[option]
					break
			year = cite['year']
			text = ['<p>']
			text.append('%s, %s, %s, %s' % (title, author, venue, year))
			text.append('<p/>')
			pre_sort.append((int(year), text))
		pre_sort.sort(reverse=True)
		for text in pre_sort:
			extra_text += text[1]
		fields['extra'] = extra_text
	# bib
	out = open(target_dir + '/pubs/' + pub['label'] + '.bib', 'w')
	bib_comb = []
	for line in pub['bib']:
		print >> out, line
		bib_comb.append(line)
	out.close()
	fields['bib'] = '\n'.join(bib_comb)

	# use the fields to construct the html for this publication
	text = []

	if 'url' in pub:
		fields['url'] = pub['url']
		text.append('<a href="%(url)s">%(title)s</a>' % fields)
	elif 'paper' in pub['files']:
		text.append('<a href="pubs/%s_%s">%s</a>' % (pub['label'], pub['files']['paper'], fields['title']))
	else:
		text.append('%(title)s' % pub)
	text.append('<br />')
	text.append('%(author)s' % fields)
	text.append('<br />')
	text.append('%(venue)s, %(date)s' % fields)
	if 'pages' in fields:
		text[-1] += ', pages %(pages)s' % fields

	text.append('<br />')
	if 'software' in fields:
		text.append('<a href="%s">[software]</a>&nbsp;&nbsp;' % (fields['software']))
	if 'url' in fields:
		text.append('<a href="%s">[paper]</a>&nbsp;&nbsp;' % (fields['url']))
	for ending in pub['files']:
		if ending == 'paper' and 'url' in fields:
			continue
		text.append('<a href="pubs/%s_%s">[%s]</a>&nbsp;&nbsp;' % (pub['label'], pub['files'][ending], ending))


	for line in ('''<a href="javascript:;" onClick="
if (document.getElementById('bib%(num)s').style.display == 'block') {
document.getElementById('bib%(num)s').style.display='none';
} else {
document.getElementById('bib%(num)s').style.display='block';
}
">[bib]</a>
&nbsp;&nbsp;
<a href="javascript:;" onClick="
if (document.getElementById('extra%(num)s').style.display == 'block') {
document.getElementById('extra%(num)s').style.display='none';
} else {
document.getElementById('extra%(num)s').style.display='block';
}
">[other info]</a>
<div id="bib%(num)s" style="display: none;margin-left:-40px;" style="text-align:right;">
\t<blockquote>
\t\t<code>''' % fields).split('\n'):
		text.append(line)
	text.append('''\t\t\t<pre>\n%(bib)s''' % fields)
	for line in ('''\t\t\t</pre>
\t\t</code>
\t</blockquote>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="pubs/%(label)s.bib">bib as a file</a>
</div>
''' % fields).split('\n'):
		text.append(line)

	for line in('''<div id="extra%(num)s" style="display: none;margin-left:20px;" style="text-align:right;">
\t<p>''' % fields).split('\n'):
		text.append(line)
	for line in fields['extra']:
		text.append('\t\t\t' + line)
	for line in ('''\t</p>
</div>
''' % fields).split('\n'):
		text.append(line)

	return text

def get_pub_info(data_dir, target_dir):
	info = get_pub_info_for_file(data_dir + '/pubs/publications.bib', data_dir, target_dir)
	for label in info:
		pub = info[label]
		pub['citing_pubs'] = get_pub_info_for_file(data_dir + '/pubs/' + label + '/citations.bib', data_dir, target_dir)
		pub['html'] = gen_html(pub, target_dir)
	return info

def get_pub_info_for_file(filename, data_dir, target_dir):
	pubs = {}
	if len(glob.glob(filename)) == 0:
		return pubs

	cur = None
	num = 0
	for line in open(filename, 'rU'):
		if len(line) > 0:
			line = line[:-1]
		if len(line) > 0:
			if line[0] == '}':
				cur['bib'].append(line)
				pubs[cur['label']] = cur
				cur = None
			elif line[0] == '@':
				cur = {'html': ''}
				cur['bib'] = []
				label = '_'.join(line.split('{')[1][:-1].split(':'))
				cur['label'] = label
				# check to see what files we have for this paper
				file_endings = [name.split(label + '_')[1] for name in glob.glob("%s/pubs/%s/%s_*" % (data_dir, label, label))]
				cur['files'] = {}
				for ending in file_endings:
					cur['files'][ending.split('.')[0]] = ending
				cur['num'] = str(num)
				num += 1
			elif '=' in line:
				nline = line.strip().split(' = ')
				data = nline[1][1:-1]
				if data[-1] == '}':
					data = data[:-1]
				cur[nline[0].strip()] = data
		if cur is not None:
			cur['bib'].append(line)
	return pubs

def replace_pub_ref(line, config, page_name, url_base, target_dir, pub_info):
	ans = []
	if "%(pubs)s" in line:
		pubs = {}
		for pub in pub_info:
			info = pub_info[pub]
			if info['year'] not in pubs:
				pubs[info['year']] = []
			pubs[info['year']].append(info)
		years = pubs.keys()
		years.sort(reverse=True)
		for year in years:
			ans.append('<h4>%s</h4>' % year)
			ans.append('<div style="margin-left:60px;margin-top:-40px;">')
			for info in pubs[year]:
				ans.append('<p style="margin:0px 0px 10px 0px;">')
				ans += info['html']
				ans.append('</p>')
			ans.append('</div>')
	else:
		label = '_'.join(line[6:-2].split(':'))
		if label not in pub_info:
			print label, "is not a valid publication label"
		info = pub_info[label]
		ans.append('<p>')
		ans += info['html']
		ans.append('</p>')
	return ans
