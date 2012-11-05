#!/usr/bin/env python

import sys, glob, os
from page_gen import *
from pub_gen import *

if __name__ == '__main__':
	# Config
	config = {
		'target_dir': './',
		'data_dir': '/home/jonathan/Dropbox/jkk_name_data/',
		'url_base': '',
		'page_template': 'templates/base.html'
	}
	if len(sys.argv) == 2:
		for line in open(sys.argv[1]):
			line = line.strip()
			if line == '' or line[0] == '#':
				continue
			parts = line.split('=')
			key = parts[0].strip()
			value = parts[1].strip()
			if value.strip() != '':
				if ':' in value:
					config[key] = {}
					for pair in value.split(' '):
						pair = pair.split(':')
						config[key][pair[0]] = pair[1]
				elif ' ' in value:
					config[key] = []
					for part in value.split(' '):
						config[key].append(part)
				else:
					config[key] = value

	target_dir = config['target_dir']
	data_dir = config['data_dir']
	url_base = config['url_base']

	pages = [name for name in glob.glob(data_dir + '/pages/*')]
	if 'page_order' not in config:
		page_order = []
		for page in pages:
			if '.html' in page:
				page = page[:-5]
			page_order.append(page)
		config['page_order'] = page_order
	
	print "Running with:"
	for key in config:
		print key + '\t' + config[key].__str__()
	print


	# Clean up the target space
	if len(glob.glob(target_dir)) != 0:
		os.system('rm -r %s/docs' % target_dir)
		os.system('rm -r %s/images' % target_dir)
		os.system('rm -r %s/pubs' % target_dir)
	#os.system('mkdir %s' % target_dir)
	os.system('mkdir %s/docs' % target_dir)
	os.system('mkdir %s/images' % target_dir)
	os.system('mkdir %s/pubs' % target_dir)
	os.system('cp %s/templates/* %s/.' % (data_dir, target_dir))
	os.system('cp -R %s/images/* %s/images/.' % (data_dir, target_dir))
	os.system('cp -R %s/docs/* %s/docs/.' % (data_dir, target_dir))
	os.system('cp -R %s/pubs/publications.bib %s/pubs/jonathan_k_kummerfeld_publications.bib' % (data_dir, target_dir))
	os.system('rm -rf %s/pubs/citations*' % (target_dir))
	os.system('cp -R %s/pubs/*/*_talk* %s/pubs/.' % (data_dir, target_dir))
	os.system('cp -R %s/pubs/*/*_poster* %s/pubs/.' % (data_dir, target_dir))

	# Construct publication info
	pub_info = pub_gen.get_pub_info(data_dir, target_dir)
	for pub in pub_info:
		if 'url' not in pub_info[pub]:
			os.system('cp -R %s/pubs/%s/* %s/pubs/.' % (data_dir, pub, target_dir))

	# Construct pages
	page_template = open(data_dir + '/' + config['page_template']).readlines()
	for page_location in pages:
		page_content = open(page_location).readlines()
		page_name = page_location.split('/')[-1]
		print 'Generating', page_name
		gen_page(page_template, page_content, config, page_name, url_base, target_dir, pub_info)

