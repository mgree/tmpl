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
    """
    A class used to parse the ACM's XML DL.

    Usage:

        Instantiating a Parser:

        To instantiate a Parser, you need to pass in the directory containing
        the XML files to parse:
        
            parser = Parser(
                directory='/Users/smacpher/clones/tmpl_venv/proceedings'
            )

        Using a Parser:

        There are two different ways to use a Parser object:
            1) call parse(). Returns a generator that yield the extracted
               papers and conference objects dynamically in memory in the
               form (conference json obj, paper json obj):

                docGenerator = parser.parse()

            2) call parseToDisk(). Parses and writes the papers and
               conference metadata to disk, organizing them into a main
               directory (path given as a param to the method) with
               subdirectories corresponding to the extracted papers
               and metadata from a conference in a specific year:

                parser.parseToDisk()

    Args:
        directory: path to the directory containing the ACM XML proceedings.
        toDisk: whether to write to disk or return a generator.
            Set to True to write to disk.
        destDir: if toDisk is set to true, destination directory to
            write parsed DL to.
        conferences: iterable of conferences to parse. Defaults to the
            Big 4 PL conferences.
        parentLogger: logger to use in the Parser instance.
            If None, a new Parser object will be instantiated for the
            Parser instance.
    """
    def __init__(self, directory,
                 conferences={'POPL', 'PLDI', 'ICFP', 'OOPSLA'},
                 parentLogger=None):
        self.directory = directory
        self.conferences = conferences

        if parentLogger:
            self.logger = parentLogger.getChild('Parser')
        else:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('Parser')
            self.logger = logger

    def parse(self):
        """
        Parses desired conferences and returns a generator that yields
        papers and their respective conference metadata in the form
        (conference json obj, paper json obj).
        """
        self.logger.info(
            'Parsing DL XML files from \'{directory}.\''.format(
                directory=self.directory
            )
        )
        for filename in tqdm(os.listdir(self.directory)):
            if not filename.endswith('.xml'):
                continue

            # Parse conference and year from filename so that if it's not
            # a conference we care about, we don't have to waste
            # time by reading its XML file. 
            conference, year = Parser._getConferenceAndYear(filename)

            # Not a conference that we care about so skip it.
            if conference not in self.conferences:
                continue

            self.logger.debug(
                'Reading {conference} {year} from \'{filename}\''.format(
                    conference=conference,
                    year=year,
                    filename=filename,
                )
            )

            curConference = None

            for obj in Parser._parseXML(self.directory,
                                        os.path.join(self.directory, filename)):
                if 'series_id' in obj:  # Found the conference object.
                    curConference = obj
                else:  # Found a paper.
                    yield (curConference, obj)

    def parseToDisk(self, destDir):
        """
        Parses all conferences in the given directory.
        Writes papers and metadata from each conference to a respective
        directory per conference. Sample output directory structure:

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
            destDir: path to the destination directory to parse to.
                Creates it if needed.
        """
        makeDir(destDir)

        # Keep track of the number of papers found per
        # conference and year for metric purposes.
        confPaperCounts = dict()

        curConference = None
        curOutDir = None
        paperNum = 0
        for (conference, paper) in tqdm(self.parse()):
            # First conference or found a new conference. 
            # Write new conference to disk.
            if (curConference is None or
                conference.get('proc_id') != curConference.get('proc_id')):

                # Update previous conference's paper count and log metrics.
                if curConference is not None:
                    confPaperCounts[curConference.get('acronym')] = paperNum

                # Update curConference to reflect new conference.
                curConference = conference
                confPaperCounts[curConference.get('acronym')] = 0
                paperNum = 0
                curOutDir = os.path.join(destDir, curConference.get('acronym'))

                # Write conference metadata.
                makeDir(curOutDir)
                with codecs.open(
                    os.path.join(curOutDir, 'metadata.json'),
                    'w',
                    'utf8'
                ) as f:
                    f.write(json.dumps(curConference))

            # Write paper. Increment paperNum counter to ensure unique
            # filename for next paper.
            with codecs.open(
                os.path.join(curOutDir, '{i}.json'.format(i=paperNum)),
                'w',
                'utf8',
            ) as f:
                f.write(json.dumps(paper))

            paperNum += 1

        self.logger.info(
            (
                'Finished parsing and writing '
                'papers to disk at \'{destDir}\''
            ).format(destDir=destDir)
        )
        self.logger.debug(
            '{metrics}.'.format(
                metrics='\n'.join(
                    [conf + ': ' + str(n) + ' papers'
                     for conf, n in confPaperCounts.iteritems()]
                )
            )
        )
        self.logger.info(
            'Found {numPapers} papers.'.format(
                numPapers=sum(confPaperCounts.itervalues())
            )
        )

    @staticmethod
    def _parseXML(procDir, filepath):
        """
        Parses one XML file containing the proceedings for a
        given conference and year.

        Args:
            procDir: proceeding dir representing one conference and year to
                write conference metadata to.
            filepath: filepath of proceeding to parse; represents
                one conference and year.

        Returns:
            A generator that writes the current proceeding's metadata to
            procDir and yields papers from that conference.
        """
        xmlParser = ElementTree.XMLParser()
        xmlParser.parser.UseForeignDTD(True)
        xmlParser.entity = Parser._AllEntities()

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
            'year': proceeding.findtext('copyright_year'),
        }

        yield conferenceData

        conference, year = Parser._getConferenceAndYear(
            os.path.basename(filepath)
        )
        for node in root.iter('article_rec'):
            # Two unique identifiers for papers.
            # DOI is a good global identifier, however, not all papers have it.
            articleId = node.findtext('article_id')
            doiNumber = node.findtext('doi_number')
            url = node.findtext('url')
            articlePublicationDate = node.findtext('article_publication_date')

            # Build title string.
            # (some papers split up title into <title>:<subtitle>
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
                    # Parse out full name.
                    # Note: only last_name is a required field.
                    author['name'] = ' '.join(
                        filter(
                            lambda s: s != '', 
                            [au.findtext('first_name'),
                             au.findtext('middle_name'),
                             au.findtext('last_name')]
                        )
                    )
                    # Parse out other important metadata
                    # that help distinguish authors.
                    author['person_id'] = au.findtext('person_id')
                    author['author_profile_id'] = au.findtext(
                        'author_profile_id'
                    )
                    author['orcid_id'] = au.findtext('orcid_id')
                    author['affiliation'] = au.findtext('affiliation')
                    author['email_address'] = au.findtext('email_address')
                    authors.append(author)

            # Find abstract.
            abstract = ''
            abs_node = node.find('abstract')
            if abs_node is not None:
                abstract = '\n'.join(filter(lambda s: s != '',
                                            [par.text for
                                             par in abs_node.findall('par')]))

            # Find full text.
            fulltext = ''
            fulltext_node = node.find('fulltext')
            if fulltext_node is not None:
                body = fulltext_node.find('ft_body')
                if body is not None:
                    fulltext = body.text

            if procId is None:
                self.logger.ERROR(
                    (
                        '\'proc_id\' is None for {title} '
                        'in {conference}-{year}'
                    ).format(
                        title=title,
                        conference=conference,
                        year=year
                    )
                )

            yield {'conference': conference,
                   'year': year,
                   'article_id': articleId,  # unique key to identify paper.
                   'proc_id': procId,  # key to identify paper's conference
                   'url': url,
                   'article_publication_date': articlePublicationDate,
                   'doi_number': doiNumber,
                   'title': title,
                   'authors': authors,
                   'abstract': abstract,
                   'fulltext': fulltext}

    @staticmethod
    def _getConferenceAndYear(filename):
        """
        Fetches the conference and year from a filename of the form
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

    class _AllEntities:
        def __init__(self):
            pass

        def __getitem__(self, key):
            return key


if __name__ == '__main__':
    """
    You can also use this parser class to manually parse the XML DL files
    into a desired directory on disk. When developing Tmpl,
    this can be useful to save time when running model
    after model. That way, you'll only have to parse the DL once and
    use the Reader class (which has an option to use a Parser and
    read directly from the XML DL files) to read the parsed version in.
    
    Usage:
        (via the command line)

            smacpher$ python parser.py ~/clones/tmpl_venv/acm-data/proceedings/
        
        Note: since no '--output_dir' was specified, the output is written
            to the default location, 'parsed/', in the current
            working directory.

        You can also specify an output directory like in the following command:
            smacpher$ python parser.py ~/clones/tmpl_venv/acm-data/proceedings/
                --output_dir ~/parsed
    """

    parser = ArgumentParser(
        description=(
            'Used to parse the XML files of the ACM DL. '
            'Output directory is organized into subdirectories '
            'by conference-year.'
        ),
        epilog='Happy parsing!',
    )

    parser.add_argument(
        'dl_dir', type=str,
        help=(
            'The path to the ACM proceedings'
            'directory containing the XML DL files.'
        )
    )
    parser.add_argument(
        '-o','--output_dir', type=str, default='./parsed', required=False,
        help=(
            'The path of the directory to '
            'save the parsed DL files to. Defaults to "./parsed".'
        )
    )
    parser.add_argument(
        '-c', '--conferences', dest='conferences', nargs='*',
        help='List of conferences that you want to parse (eg. -c POPL OOPSLA).'
    )

    args = parser.parse_args()
    DL_DIR = args.dl_dir
    DEST_DIR = args.output_dir
    CONFERENCES = args.conferences

    if CONFERENCES is None:
        parser = Parser(directory=DL_DIR)
    else:
        parser = Parser(directory=DL_DIR, conferences=set(CONFERENCES))

    parser.parseToDisk(DEST_DIR)
