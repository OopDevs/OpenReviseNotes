"""
mkcourses.py

Make the courses/chapters list for OpenRevise.

Can be imported as a library. Refer to docs/mkchapters.html

Copyright (C) 2020-present jkelol111
"""

__author__ = 'jkelol111'
__copyright__ = 'Copyright (C) 2020-present jkelol111'
__license__ = 'Public Domain'
__version__ = '1.0'

import os
import shutil
import time
import sys
import json
import threading
import pprint
import argparse
import logging

class Courses:
    """
    Utilities to scan for chapters
    """
    def __init__(self, directory, dryrun):
        self.dryrun = dryrun
        self.directory = directory
        self.everything = {}
        self.refresh_courses()

    def start_thread(self, function):
        """
        Starts a new Thread for moar performance.
        """
        t = threading.Thread(target=function)
        t.start()

    def refresh_courses(self, threaded=False):
        def task_refresh_courses():
            total_files = 0
            for course in os.scandir(self.directory):
                if not course.name.startswith('.') and course.is_dir():
                    logging.debug('Found course: ' + course.name)
                    self.everything[course.name] = {}
                    for chapter in os.scandir(os.path.join(self.directory, course.name)):
                        if not chapter.name.startswith('.') and chapter.is_dir():
                            self.everything[course.name][chapter.name] = {}
                            for file in os.scandir(os.path.join(self.directory, course.name, chapter)):
                                if not file.name.startswith('.') and file.is_file():
                                    file_extension = os.path.splitext(file.name)[1].split('.')[1]
                                    if not file_extension in self.everything[course.name][chapter.name]:
                                        self.everything[course.name][chapter.name][file_extension] = []
                                    if not self.everything[course.name][chapter.name][file_extension]:
                                        self.everything[course.name][chapter.name][file_extension] = []
                                    self.everything[course.name][chapter.name][file_extension].append(file.name)
                                    total_files += 1
            logging.info('Found {0} files!'.format(total_files))
        if threaded:
            self.start_thread(task_refresh_courses)
        elif not threaded:
            task_refresh_courses()

    def get_courses(self, threaded=False):
        """
        Returns the list of chapters/files, depending on argument

        Returns an empty array if there are no courses.
        """
        def task_get_courses():
            courses = []
            for course in self.everything:
                courses.append(str(course))
            return courses
        if threaded:
            self.start_thread(task_get_courses)
        elif not threaded:
            task_get_courses()

    def get_course_chapters(self, course):
        if course in self.everything:
            return self.everything[course]
        else:
            raise TypeError('"{0}" is not in the courses list!'.format(course))

    def write_courses(self, threaded=False):
        pass


# Run only if the file isn't imported
if __name__ == '__main__':
    # Prints standard copyright stuff.
    print('{file} (version: {version})'.format(
        file=__file__,
        version=__version__
    ))
    print(__copyright__)
    print('-----------------------------------------------')
    # Scan for command line arguments
    CMD_PARSER = argparse.ArgumentParser(
        description='Generate the chapters.json and courses.json database for OpenRevise.'
    )
    CMD_PARSER.add_argument(
        'command',
        action='store',
        help='The command to run (generate, list)')

    CMD_PARSER.add_argument(
        '--force-directory',
        action='store',
        dest='forced_directory',
        help='The directory the notes folder. If this is not provided, the "notes" folder in the\
              same directory will be used.')
    CMD_PARSER.add_argument(
        '-d', '--dryrun',
        action="store_true",
        default=False,
        help='Dry run / perform the command without actually changing anything.')
    CMD_PARSER.add_argument(
        '-D', '--debug',
        action="store_true",
        default=False,
        help='Activates enhanced logging.')
    CMD_PARSED = CMD_PARSER.parse_args()
    print('Command parsed: ' + CMD_PARSED.command)
    if CMD_PARSED.forced_directory is not None:
        print('Forced directory parsed: ' + CMD_PARSED.forced_directory)
    else:
        print('Forced directory not specified, skipping.')
    print('Dry run parsed: ' + str(CMD_PARSED.dryrun))
    print('Debug logging: ' + str(CMD_PARSED.debug))
    print('-----------------------------------------------')
    if CMD_PARSED.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.info('Selected task: {0}\n'.format(CMD_PARSED.command))
    if CMD_PARSED.command in ['generate', 'list']:
        if CMD_PARSED.forced_directory is not None:
            logging.info('0/x: Scanning forced directory: ' + CMD_PARSED.forced_directory)
            SCANNER = Courses(CMD_PARSED.forced_directory, CMD_PARSED.dryrun)
        else:
            logging.info('0/x: Scanning notes/ directory...')
            SCANNER = Courses(os.path.join(os.getcwd(), 'notes'), CMD_PARSED.dryrun)
    if CMD_PARSED.command == 'generate':
        logging.info('1/2: Compiling the JSON...')
        print('\n')
        if CMD_PARSED.forced_directory is not None:
            logging.info('2/2: Writing {0}/courses.json...'.format(CMD_PARSED.forced_directory))
        else:
            logging.info('2/2: Writing notes/courses.json...')
    elif CMD_PARSED.command == 'list':
        print()
        logging.info('1/1: Listing courses and associated files...')
        pprint.pprint(SCANNER.everything)
    print('\n\nAll done!')
