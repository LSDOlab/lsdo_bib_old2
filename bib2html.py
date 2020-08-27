from __future__ import division, print_function
from six import iteritems

from pybtex.database.input import bibtex
import pybtex


class Bib2Html(object):

    def __init__(self):
        self.bib_dict = self._read_bib_file()
        self._write_bib_files()

        self.header = \
        r"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <title>Bootstrap Example</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js"></script>
        <style>
        /* Make the image fully responsive */
        .carousel-inner img {
            width: 100%;
            height: 100%;
        }
        </style>
        </head>
        <body>
        """
        self.heading = \
        r"""
        <h3 id="h.p_wWsYqgOg8L8R" class="zfr3Q JYVBee">{}</h3>
        """

    def _read_bib_file(self):
        with open('lsdo.bib', 'r') as f:
            bib_string = f.read()

        bib_dict = pybtex.database.parse_string(bib_string, 'bibtex')

        return bib_dict

    def _write_bib_files(self):
        for key, ref in iteritems(self.bib_dict.entries):
            bib_data = pybtex.database.BibliographyData({key: ref})
            bib_string = bib_data.to_string('bibtex')

            with open('individual_bib_files/{}.bib'.format(key), 'w') as f:
                f.write(bib_string[:-1])

    def _write_line(self, key, ref, prefix):
        line = ''
        line += prefix

        # Paper author
        authors_list = ref.persons.values()[0]
        for ind, author in enumerate(authors_list):

            first_names = ' '.join(author.bibtex_first_names)
            last_names = ' '.join(author.last_names)

            work = first_names

            # Turn all full words into single letters
            work = work.split(' ')
            for k in range(len(work)):
                if len(work[k]) > 1 and work[k][1] != '.':
                    work[k] = work[k][0]
            work = ' '.join(work)

            # Remove all periods
            work = work.replace('.', '')

            # Replace all spaces with '. '
            work = work.split(' ')
            work = '. '.join(work)

            # Add a final period
            work = work + '.'

            first_names = work

            # Build string with the format, 'Last, First M.'
            name = last_names + ', ' + first_names

            # Append ' Last, First M.'
            line += ' '
            line += name
            line += ','

            # If second last entry, append ' and'
            if ind == len(authors_list) - 2:
                line += ' and'

        # Paper title
        line += ' <q>{},</q>'.format(ref.fields['title'])

        # Journal papers:
        if ref.type == 'article':
            if 'journal' in ref.fields:
                line += ' <i>{}</i>,'.format(ref.fields['journal'])
            if 'volume' in ref.fields:
                line += ' Vol. {},'.format(ref.fields['volume'])
            if 'number' in ref.fields:
                line += ' No. {},'.format(ref.fields['number'])
            if 'year' in ref.fields:
                line += ' {},'.format(ref.fields['year'])
            if 'pages' in ref.fields:
                line += ' pp. {},'.format(ref.fields['pages'])
            line = line[:-1] + '.'

        # Conference papers:
        elif ref.type == 'inproceedings':
            if 'booktitle' in ref.fields:
                line += ' <i>{}</i>,'.format(ref.fields['booktitle'])
            line = line[:-1] + '.'
            if 'aiaa' in ref.fields:
                line += ' (AIAA {}-{})'.format(ref.fields['year'], ref.fields['aiaa'])

        bibtex_link = 'https://lsdolab.github.io/lsdo_bib/individual_bib_files/{}.bib'.format(key)
        line += ' <a href="{}">[bibtex]</a>'.format(bibtex_link)

        doi = ref.fields.get('doi', None)
        if doi is not None and doi[:4] != 'http':
            doi = 'http://doi.acm.org/{}'.format(doi)
        if doi is not None:
            line += ' <a href="{}">[doi]</a>'.format(doi)

        pdf = ref.fields.get('pdf', None)
        if pdf is not None:
            line += ' <a href="{}">[pdf]</a>'.format(pdf)

        return line

    def _get_lines(self, ref_type=None, year=None, prefix=''):
        counter = 0
        for key, ref in iteritems(self.bib_dict.entries):
            desired_type = ref_type is None or ref.type == ref_type
            desired_year = year is None or ref.fields['year'] == year
            if desired_type and desired_year:
                counter += 1

        index = counter

        lines = []
        lines.append('<ul style="line-height:200%">')

        for key, ref in iteritems(self.bib_dict.entries):
            desired_type = ref_type is None or ref.type == ref_type
            desired_year = year is None or ref.fields['year'] == year
            if desired_type and desired_year:
                line = self._write_line(key, ref, prefix.format(index))
                lines.append('  <li>{}</li>'.format(line))
                index -= 1

        lines.append('</ul>')

        return lines

    def write_html_by_type(self):        
        code = ''
        code += self.header 
        code += self.heading.format('Journal papers')
        code += '\n'.join(self._get_lines(ref_type='article', prefix='[J{}]'))
        code += self.heading.format('Conference papers')
        code += '\n'.join(self._get_lines(ref_type='inproceedings', prefix='[J{}]'))

        with open ('bib_by_type.html', 'w') as f:
            keys = f.write(code)

    def write_html_by_year(self):
        code = ''
        code += self.header 
        for year in [2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012]:
            code += self.heading.format(str(year))
            code += '\n'.join(self._get_lines(year=str(year)))

        with open ('bib_by_year.html', 'w') as f:
            keys = f.write(code)


if __name__ == '__main__':
    b2h = Bib2Html()
    b2h.write_html_by_type()
    b2h.write_html_by_year()