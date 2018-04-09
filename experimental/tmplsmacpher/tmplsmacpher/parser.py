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
    logger.setLevel(logging.INFO)

    @staticmethod
    def parseDir(dirPath, destDir='.', conferences={'POPL', 'PLDI', 'ICFP', 'OOPSLA'}, noOp=False):
        """Parses all conferences in a given directory. Writes papers and metadata from each conference
        to a respective directory per conference.

        Args:
            dirPath: path to raw DL (digital library) xml files to parse.
            destDir: destination dir to parse to. Defaults to current directory.
            conferences: conferences to parse.
            noOp: whether to run a dry run or not. If noOp is set to True, will not actually write results.
        """
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
            for i, paper in enumerate(Parser.parseXML(curOutputDir, os.path.join(dirPath, filename))):
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
    def parseXML(procDir, filepath):
        """Parses one XML file containing the proceedings for a given conference and year.

        Args:
            procDir: proceeding dir representing one conference and year to write conference metadata to.
            filepath: filepath of proceeding to parse; represents one conference and year.

        Returns:
            A generator that writes the current proceeding's metadata to procDir and yields papers from that conference.
        """
        xmlParser = ElementTree.XMLParser()
        xmlParser.parser.UseForeignDTD(True)
        xmlParser.entity = Parser.AllEntities()

        elementTree = ElementTree.ElementTree()

        elementTree.parse(filepath, parser=xmlParser)
        root = elementTree.getroot()

        # Fetch metadata for conference and write to file.
        series = root.find('series_rec').find('series_name')
        proceeding = root.find('proceeding_rec')
        procId = Parser.writeConferenceMetadata(procDir, series, proceeding)

        conference, year = Parser.getConferenceAndYear(os.path.basename(filepath))
        for node in root.iter('article_rec'):
            # Two unique identifiers for papers; DOI is global, however, not all papers have it.
            articleId = node.findtext('article_id')
            doiNumber = node.findtext('doi_number')
            url = node.findtext('url')
            articlePublicationDate = node.findtext('article_publication_date')

            # Build title string. (some papers split up title into <title>:<subtitle>
            title = node.findtext('title')
            subtitle = node.findtext('subtitle')
            title += ': ' + subtitle if subtitle is not None else ''
            title = title.translate(None, '\"') # Remove quotes (") from title.

            # Find authors.
            authors = []
            author_node = node.find('authors')
            if author_node is not None:
                for au in author_node.findall('au'):
                    author = dict()
                    # Parse out full name. (note: only last_name is a required field)
                    author['name'] = ' '.join(filter(lambda s: s != '', [au.findtext('first_name'),
                                                                         au.findtext('middle_name'),
                                                                         au.findtext('last_name')]))
                    # Parse out other important metadata that help distinguish authors.
                    author['person_id'] = au.findtext('person_id')
                    author['author_profile_id'] = au.findtext('author_profile_id')
                    author['orcid_id'] = au.findtext('orcid_id')
                    author['affiliation'] = au.findtext('affiliation')
                    author['email_address'] = au.findtext('email_address')
                    authors.append(author)

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

            if procId is None:
                logging.ERROR("PROC_ID is None for {title} in {conference}-{year}".format(title=title, conference=conference, year=year))
            yield {'conference': conference,
                   'year': year,
                   'article_id': articleId,  # unique key to identify this paper.
                   'proc_id': procId,  # key to identify which proceeding this paper was in.
                   'url': url,
                   'article_publication_date': articlePublicationDate,
                   'doi_number': doiNumber,
                   'title': title,
                   'authors': authors,
                   'abstract': abstract,
                   'fulltext': fulltext}

    @staticmethod
    def getConferenceAndYear(filename):
        """Fetches the conference and year from a filename of the form
        'PROC-POPL00-2000-325694.xml'

        Args:
            filename: filename to extract conference and year from.

        Returns:
            Conference, year
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
    def writeConferenceMetadata(outputDir, series, proceeding):
        """ Writes metadata for one conference for one year.

        Args:
            outputDir: output directory representing conference and year to write metadata to.
            series: series ElementTree node to extract series metadata from.
            proceeding: proceeding ElementTree node to extract proceeding metadata from.
        """
        filename = 'metadata.txt'
        procId = proceeding.findtext('proc_id')
        metadata = {
            'series_id': series.findtext('series_id'),
            'series_title': series.findtext('series_title'),
            'series_vol': series.findtext('series_vol'),
            'proc_id': procId,
            'proc_title': proceeding.findtext('proc_title'),
            'acronym': proceeding.findtext('acronym'),
            'isbn13': proceeding.findtext('isbn13'),
            'year': proceeding.findtext('copyright_year'),  # may have to revert back to using year parsed from filename
        }

        with codecs.open(os.path.join(outputDir, filename), 'w', 'utf8') as f:
            f.write(json.dumps(metadata))
        return procId

    class AllEntities:
        def __init__(self):
            pass

        def __getitem__(self, key):
            return key


if __name__ == '__main__':
    DL_DIR = '/Users/smacpher/clones/tmpl_venv/acm-data/proceedings'
    OUT_DIR = '/Users/smacpher/clones/tmpl_venv/acm-data/parsed'
    parser = Parser()
    parser.parseDir(DL_DIR, destDir=OUT_DIR, noOp=False)
