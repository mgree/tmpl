import codecs
import json
import logging
import os

from argparse import ArgumentParser
from tqdm import tqdm
from xml.etree import ElementTree

from utils import getLoggingFormatter
from utils import makeDir


class Parser(object):
    """Use to parse the DL."""

    """Constructor for Parser object.
    
    Usage:
        There are two different ways to use a Parser object:
        1) use it to read in the ACM DL XML files and yield the extracted paper and 
        conference objects dynamically in memory.
        2) use it to parse the ACM DL XML files and write them to disk, organizing
        them into a given directory with subdirectories corresponding to the extracted papers
        and metadata from a conference in a specific year.

    Args:
        dlDir: path to the directory containing the ACM XML proceedings.
        toDisk: whether to write to disk or return a generator. Set to True to write to disk.
        destDir: if toDisk is set to true, destination directory to write parsed DL to.
        conferences: iterable of conferences to parse. Defaults to the big 4 PL conferences.
        parentLogger: logger to use in the Parser instance. If None, a new Parser object will
            be instantiated for the Parser instance.  
    """
    def __init__(self, dlDir, conferences={'POPL', 'PLDI', 'ICFP', 'OOPSLA'}, parentLogger=None):
        self.dlDir = dlDir
        self.conferences = conferences

        if parentLogger:
            self.logger = parentLogger.getChild('Parser')
        else:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('Parser')
            self.logger = logger

    def parse(self):
        """Parses desired conferences and returns a generator that yields papers and their respective conference metadata.

        Args:
            dlDir: path to raw DL (digital library) xml files to parse.
            destDir: destination dir to parse to. Defaults to current directory.
            conferences: conferences to parse.
            noOp: whether to run a dry run or not. If noOp is set to True, will not actually write results.
        """
        self.logger.info('Parsing DL XML files at {dlDir}.'.format(dlDir=self.dlDir))
        for filename in tqdm(os.listdir(self.dlDir)):
            if not filename.endswith('.xml'):
                continue

            # Parse conference and year from filename so that if it's not 
            # a conference we care about, we don't have to waste time by reading its XML file. 
            conference, year = Parser.getConferenceAndYear(filename)

            # Not a conference that we care about so skip it.
            if conference not in self.conferences:
                continue

            self.logger.debug('Reading {conference} {year} from {filename}'.format(
                conference=conference,
                year=year,
                filename=filename,
                )
            )

            curConference = None

            for obj in Parser.parseXML(self.dlDir, os.path.join(self.dlDir, filename)):
                if 'series_id' in obj: # Found the conference object.
                    curConference = obj
                else: # Found a paper. Pair it with its respective conference's metadata and yield.
                    yield (curConference, obj)

    def parseToDisk(self, destDir):
        """Parses all conferences in the given directory. Writes papers and metadata from each conference
        to a respective directory per conference. Sample output directory structure:

        parsed/
            OOPSLA '87/
                0.json
                1.json
                2.json
                ... etc.
                99.json
                metadata.json
            ... etc.
            POPL '73/
                0.json
                1.json
                ... etc.
                32.json
                metadata.json
            ... etc.

        Where 'parsed/' is the destDir, 'i.json' files are papers, and 
        'metadata.json' files are conference metadata.

        Args:
            destDir: path to the destination directory to parse to. Creates it if needed.
        """
        makeDir(destDir)

        # Keep track of the number of papers found per conference and year for metric purposes.
        numPapersPerConference = dict()

        curConference = None
        curOutDir = None
        paperNum = 0
        for (conference, paper) in self.parse():
            # First conference or found a new conference. Write new conference to disk.
            if curConference is None or conference.get('proc_id') != curConference.get('proc_id'):
                # Update previous conference's paper count and log metrics.
                if curConference is not None:
                    numPapersPerConference[curConference.get('acronym')] = paperNum

                # Update curConference to reflect new conference.
                curConference = conference
                numPapersPerConference[curConference.get('acronym')] = 0
                paperNum = 0
                curOutDir = os.path.join(destDir, curConference.get('acronym'))

                # Write conference metadata.
                makeDir(curOutDir)
                with codecs.open(os.path.join(curOutDir, 'metadata.json'), 'w', 'utf8') as f:
                    f.write(json.dumps(curConference))

            # Write paper. Increment paperNum counter to ensure unique filename for next paper.
            with codecs.open(os.path.join(curOutDir, '{i}.json'.format(i=paperNum)), 'w', 'utf8') as f:
                f.write(json.dumps(paper))
            paperNum += 1

        self.logger.debug('Finished parsing. \n{metrics}.'.format(
            metrics='\n'.join([acronym + ': ' + str(n) + ' papers' for acronym, n in numPapersPerConference.iteritems()])
            )
        )
        self.logger.info('Found {numPapers} papers.'.format(
            numPapers=sum(numPapersPerConference.itervalues())
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

        # Fetch metadata for conference and yield.
        series = root.find('series_rec').find('series_name')
        proceeding = root.find('proceeding_rec')
        procId = proceeding.findtext('proc_id')

        conferenceData = {
            'series_id': series.findtext('series_id'),
            'series_title': series.findtext('series_title'),
            'series_vol': series.findtext('series_vol'),
            'proc_id': procId,
            'proc_title': proceeding.findtext('proc_title'),
            'acronym': proceeding.findtext('acronym'),
            'isbn13': proceeding.findtext('isbn13'),
            'year': proceeding.findtext('copyright_year'),  # may have to revert back to using year parsed from filename
        }

        yield conferenceData

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
                self.logger.ERROR("PROC_ID is None for {title} in {conference}-{year}".format(title=title, conference=conference, year=year))
            yield {'conference': conference,
                   'year': year,
                   'article_id': articleId,  # unique key to identify this paper.
                   'proc_id': procId,  # key to identify which conference this paper was in.
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
            raise e

    class AllEntities:
        def __init__(self):
            pass

        def __getitem__(self, key):
            return key


if __name__ == '__main__':
    """
    You can also use this parser class to manually parse the XML DL files
    into a desired directory. When developing Tmpl, this is probably preferred.
    That way, you'll only have to parse the DL once, and can use the Reader
    class to read the parsed version in.
    """
    parser = ArgumentParser(
        description='Used to parse the XML files of the ACM DL. Output directory is organized into subdirectories by conference-year.',
        epilog='Happy parsing!',
    )

    parser.add_argument('dl_dir', type=str,
                        help='The path to the ACM proceedings directory containing the XML DL files.')
    parser.add_argument('-o','--output_dir', type=str, default='./parsed', required=False,
                        help='The path of the directory to save the parsed DL files to. Defaults to "./parsed".')
    parser.add_argument('-c', '--conferences',
                        dest='conferences',
                        nargs='*',
                        help='List of conferences that you want to parse (eg. -c POPL OOPSLA).')

    args = parser.parse_args()
    DL_DIR = args.dl_dir
    DEST_DIR = args.output_dir
    CONFERENCES = args.conferences

    if CONFERENCES is None:
        parser = Parser(dlDir=DL_DIR)
    else:
        parser = Parser(dlDir=DL_DIR, conferences=set(CONFERENCES))

    parser.parseToDisk(DEST_DIR)
