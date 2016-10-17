# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from collections import namedtuple

import sys
from unittest2 import TestCase
import testfixtures

Tuple = namedtuple('Tuple', 'a b c')


class TestFixtures(TestCase):
    def test_readability(self):
        testfixtures.compare(expected='Cthulhu', actual='C’thalpa', prefix='Spelling counts',
                             suffix='You can bet your life on it')

    def test_longer_strings(self):
        testfixtures.compare('Ph’nglui mglw’nafh Cthulhu R’lyeh wgah’nagl fhtagn',
                             'Ph’nglui mglw’nafh Cthulhu R’lyah wgah’nagl fhtagn')

    def test_multi_line_strings(self):
        testfixtures.compare(
            '''
            O Thou that lieth dead but ever dreameth,
            Hear, Thy servant calleth Thee.
            Hear me O mighty Cthulhu!
            Hear me Lord of Dreams!
            ''',
            '''
            O Thou that lieth  dead but ever dreameth,
            Hear, Thy servant calleth Thee.\r
            Hear me O great Cthulhu!
            Hear me Lord of Dreams!
            ''',
            show_whitespace=True
        )

    def test_multi_line_strings_trailing_whitespace(self):
        testfixtures.compare(
            '''
            O Thou that lieth dead but ever dreameth,
            Hear, Thy servant calleth Thee.
            Hear me O mighty Cthulhu!
            Hear me Lord of Dreams!
            ''',
            '''
            O Thou that lieth  dead but ever dreameth,
            Hear, Thy servant calleth Thee.\r
            Hear me O great Cthulhu!
            Hear me Lord of Dreams!
            ''',
            trailing_whitespace=False
        )

    def test_multi_line_strings_blank_lines(self):
        testfixtures.compare(
            '''
            O Thou that lieth dead but ever dreameth,
            Hear, Thy servant calleth Thee.
            Hear me O mighty Cthulhu!
            Hear me Lord of Dreams!
            ''',
            '''
            O Thou that lieth  dead but ever dreameth,

            Hear, Thy servant calleth Thee.

            Hear me O great Cthulhu!


            Hear me Lord of Dreams!
            ''',
            blanklines=False
        )

    def test_set(self):
        testfixtures.compare({2, 3, 4}, {1, 2, 3})

    def test_list(self):
        testfixtures.compare([2, 3, 4], [1, 2, 3])

    def test_named_tuple(self):
        testfixtures.compare(Tuple(1, 2, 3), Tuple(a=1, b=3, c=3))

    def test_dictionary(self):
        testfixtures.compare(
            {
                'a': 1,
                'b': 2,
                'c': 3,
            },
            {
                'a': 1,
                'b': 3,
                'z': 2,
            })

    def test_recursive_comparison(self):
        testfixtures.compare(
            expected={
                'Species': 'Great Old One',
                'Title': 'The Sleeper of R\'lyeh',
                'Family': {
                    'grandpa': 'Yog-Sothoth',
                    'granda': 'Shub-Niggurath',
                    'parent': 'Nug'
                }
            },
            actual={
                'Species': 'Real Old One',
                'Title': 'The Sleeper of R\'lyeh',
                'Family': {
                    'grandpa': 'Yog-Sothoth',
                    'granda': 'Zub-Niggurath',
                    'parent': 'Nug'
                }
            })

    def test_custom_comparer(self):
        def compare_my_tuple(x, y, context):
            if x.a == y.a:
                return
            return 'Tuple named %s != Tuple named %s' % (
                context.label('x', repr(x.a)),
                context.label('y', repr(y.a)),
            )

        testfixtures.compare(Tuple(1, 2, 3), Tuple(2, 2, 3), comparers={Tuple: compare_my_tuple})

    def test_round_comparer(self):
        testfixtures.compare(testfixtures.RoundComparison(0.3, 1), 0.333)
        testfixtures.compare(testfixtures.RoundComparison(0.3, 2), 0.333)

    def test_range_comparer(self):
        testfixtures.compare(testfixtures.RangeComparison(1, 2), 1)
        testfixtures.compare(testfixtures.RangeComparison(3, 4), 1)

    def test_string_comparer(self):
        testfixtures.compare(testfixtures.StringComparison('Error no. \d+'), 'Error no. 15')
        testfixtures.compare(testfixtures.StringComparison('Error no. \d+'), 'ERROR no. 15')

    def test_logging(self):
        logger_a = logging.getLogger('A')
        logger_b = logging.getLogger('B')

        with testfixtures.LogCapture(names='A', level=logging.WARN) as log:
            logger_a.info('A message')
            logger_a.warning('A warning')

            logger_b.error('B error')
            logger_a.error('A error')

        log.check(
            ('A', 'INFO', 'A message'),
            ('A', 'WARNING', 'A warning'),
            ('A', 'ERROR', 'A error'),
        )

    def test_output(self):
        with testfixtures.OutputCapture(separate=True) as output:
            print "Hello!"
            print >> sys.stderr, "Something bad happened!"

        output.compare(stdout="Hello!", stderr="Something BAD happened!")

    def test_filesystem(self):
        with testfixtures.TempDirectory(ignore=['settings/user.txt']) as tmp_dir:
            tmp_dir.write('settings/config.txt', 'default config')
            testfixtures.compare(tmp_dir.read('settings/config.txt'), 'default config')
            tmp_dir.write('settings/user.txt', 'user config')
            tmp_dir.makedir('settings/user')
            tmp_dir.compare(
                [
                    'settings/',
                    'settings/config.txt',
                    # 'settings/user/'
                ], recursive=True, files_only=False)
            tmp_dir.cleanup()

    def test_exception(self):
        with testfixtures.ShouldRaise(ValueError('Misspelled name')):
            raise ValueError('Missing name')
