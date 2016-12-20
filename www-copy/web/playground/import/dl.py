import xml.etree.ElementTree as ET

# TODO store conference/year/unique paper ID

def nonempty(s):
    return s != ""

counter = 64

def parse_proceedings(filename):
    t = ET.parse(filename)
    root = t.getroot()
    
    for node in root.iter('article_rec'):
        # TODO article types?
       
        title = node.findtext('title')
        print title
        
        authors = []
        author_node = node.find('authors')
        if author_node is not None:
            for au in author_node.findall('au'):
                name = ' '.join(filter(nonempty,
                                       [au.findtext('first_name'),
                                        au.findtext('middle_name'),
                                        au.findtext('last_name')]))
                print name
                authors.append(name)
        
        year = ""
        year_node = node.find('ccc')
        if year_node is not None:
            copyright_node = year_node.find('copyright_holder')
            if copyright_node is not None:
                year_body = copyright_node.find('copyright_holder_year')
                if year_body is not None:
                    year = year_body.text
        print year

        abstract = ""
        abs_node = node.find('abstract')
        if abs_node is not None:
            abstract = '\n'.join(filter(nonempty,
                                        [par.text for par in abs_node.findall('par')]))

        fulltext = ""
        ft_node = node.find('fulltext')
        if ft_node is not None:
            body = ft_node.find('ft_body')
            if body is not None:
                fulltext = body.text

        if fulltext:
            global counter
            filename = "%d.txt" % (counter,)
            fo = open (filename, "wb")
            fo.write(fulltext.encode('utf8'))
            fo.close()
            counter = counter +1

        yield { 'title': title,
                'authors': authors,
                'abstract': abstract,
                'fulltext': fulltext,
                'year': year}

for i in parse_proceedings('PROC-KDD99-1999-312179.xml'):
    print 'hi'