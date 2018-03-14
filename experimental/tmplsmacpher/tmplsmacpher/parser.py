import codecs
import json
import logging
import os

from xml.etree import ElementTree

from utils import getLoggingFormatter
from utils import makeDir


class Parser(object):
    """Use to parse the DL."""

    logger = logging.getLogger('Parser')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(getLoggingFormatter())
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG)

    @staticmethod
    def getConferenceAndYear(filename):
        """Fetches the conference and year from a filename of the form
        'PROC-POPL00-2000-325694.xml'
        """
        try:
            filenameTokens = filename.split('-')
            conference = filenameTokens[1][:-2]
            year = filenameTokens[2]
            return conference, year
        except Exception as e:
            print filename
            raise e

    @staticmethod
    def parseDir(dirPath, destDir='.', conferences={'POPL', 'PLDI', 'ICFP', 'OOPSLA'}, noOp=False):
        """Parses all conferences in a given directory."""
        makeDir(destDir)

        # Keep track of the number of papers found per conference and year for metric purposes.
        numPapersPerConference = dict()
        for filename in os.listdir(dirPath):
            if not filename.endswith('.xml'):
                continue

            conference, year = Parser.getConferenceAndYear(filename)

            # Not a conference that we care about so skip.
            if conference not in conferences:
                continue

            # Make a directory for the parsed results to go.
            curOutputDir = os.path.join(destDir, conference + ' ' + year)

            if not noOp:
                makeDir(curOutputDir)

            Parser.logger.info('Parsing {conference_year}'.format(conference_year=curOutputDir))

            numPapersPerConference[(conference, year)] = 0
            for i, paper in enumerate(Parser.parseXML(os.path.join(dirPath, filename))):
                filename = '{i}.txt'.format(i=i)
                if not noOp:
                    with codecs.open(os.path.join(curOutputDir, filename), 'w', 'utf8') as f:
                        f.write(json.dumps(paper))
                Parser.logger.info('Parsed {title}'.format(title=paper['title']))
                numPapersPerConference[((conference, year))] += 1

            Parser.logger.info('Done parsing {conference} {year}. Found {numPapers} papers.'.format(
                conference=conference,
                year=year,
                numPapers=numPapersPerConference[(conference, year)])
            )

        Parser.logger.info('Done parsing {conferences}. {metrics}. \nFound {total} total papers.'.format(
            conferences=conferences,
            metrics='\n'.join([str(conf + ' ' + year) + ': ' + str(n) + ' papers'
                               for (conf, year), n in numPapersPerConference.iteritems()]),
            total=sum(numPapersPerConference.itervalues())
            )
        )

    @staticmethod
    def parseXML(filepath):
        """Parses one XML file containing the proceedings for a given conference and year."""
        xmlParser = ElementTree.XMLParser()
        xmlParser.parser.UseForeignDTD(True)
        xmlParser.entity = Parser.AllEntities()

        ET = ElementTree.ElementTree()

        ET.parse(filepath, parser=xmlParser)
        root = ET.getroot()

        conference, year = Parser.getConferenceAndYear(os.path.basename(filepath))

        for node in root.iter('article_rec'):
            # Find unique ID.
            uniqueID = node.findtext('article_id')

            # Find title.
            title = node.findtext('title')

            # Remove quotes (").
            title = title.translate(None, '\"')

            # Find authors.
            authors = []
            author_node = node.find('authors')
            if author_node is not None:
                for au in author_node.findall('au'):
                    name = ' '.join(filter(lambda s: s != '', [au.findtext('first_name'),
                                                               au.findtext('middle_name'),
                                                               au.findtext('last_name')]))
                    authors.append(name)

            # Find abstract.
            abstract = ''
            abs_node = node.find('abstract')
            if abs_node is not None:
                abstract = '\n'.join(filter(lambda s: s != '', [par.text for par in abs_node.findall('par')]))

            # Find full text.
            fulltext = ''
            fulltext_node = node.find('fulltext')
            if fulltext_node is not None:
                body = fulltext_node.find('ft_body')
                if body is not None:
                    fulltext = body.text

            yield {'conference': conference,
                   'year': year,
                   'uniqueID': uniqueID,
                   'title': title,
                   'authors': authors,
                   'abstract': abstract,
                   'fulltext': fulltext}

    class AllEntities:
        def __getitem__(self, key):
            return key


if __name__ == '__main__':
    DL_DIR = '/Users/smacpher/clones/tmpl_venv/acm-corpus/proceedings'
    OUT_DIR = '/Users/smacpher/clones/tmpl_venv/acm-corpus/parsed'
    parser = Parser()
    parser.parseDir(DL_DIR, destDir=OUT_DIR, noOp=False)