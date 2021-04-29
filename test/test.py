import unittest
import sys
import pymanifest
import os
import logging


class TestPyManifest(unittest.TestCase):
    def setUp(self):
        self.include = pymanifest.ArgSet(set(), set(), set(), set(), set())
        self.exclude = pymanifest.ArgSet(set(), set(), set(), set(), set())

        self.TEST_DATA                                  = self.__expand('./test/test_data')
        self.FILE_TXT                                   = self.__expand('./test/test_data/file.txt')
        self.FILE_EXT                                   = self.__expand('./test/test_data/file.ext')
        self.FOLDER_SUB                                 = self.__expand('./test/test_data/folder_sub')
        self.SUB_FOLDER                                 = self.__expand('./test/test_data/sub_folder')
        self.FOLDER_SUB_TEST_FILE                       = self.__expand('./test/test_data/folder_sub/test.file')
        self.FOLDER_SUB_WEIRDFILE                       = self.__expand('./test/test_data/folder_sub/weirdfile')
        self.SUB_FOLDER_FILE_TEST                       = self.__expand('./test/test_data/sub_folder/file.test')
        self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT  = self.__expand('./test/test_data/sub_folder/sub_sub_folder/another_file.txt')
        self.FILE_NO                                    = self.__expand('./test/test_data/file.no')
        self.FILE_NO2                                   = self.__expand('./test/test_data/file.no2')
        self.FOLDER_NO                                  = self.__expand('./test/test_data/folder_no')
        self.FOLDER_NO2                                 = self.__expand('./test/test_data/folder_no2')
        self.INCLUDE_MANIFEST                           = self.__expand('./test/test_manifests/manifest.txt')
        self.EXCLUDE_MANIFEST                           = self.__expand('./test/test_manifests/exclude_manifest.txt')

        # setup precheck
        folders = [
            self.FOLDER_SUB,
            self.SUB_FOLDER,
        ]

        files = [
            self.FILE_TXT,
            self.FILE_EXT,
            self.FOLDER_SUB_TEST_FILE,
            self.FOLDER_SUB_WEIRDFILE,
            self.SUB_FOLDER_FILE_TEST,
            self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT,
            self.INCLUDE_MANIFEST,
            self.EXCLUDE_MANIFEST,
        ]

        fail_files = [
            self.FILE_NO,
            self.FILE_NO2,
        ]

        fail_folders = [
            self.FOLDER_NO,
            self.FOLDER_NO2,
        ]

        for folder in folders:
            if not os.path.isdir(folder):
                logging.error(f"Incorrect test setup! Missing folder {folder}")
                sys.exit(1)

        for file in files:
            if not os.path.isfile(file):
                logging.error(f"Incorrect test setup! Missing file {file}")
                sys.exit(1)

        for folder in fail_folders:
            if os.path.isdir(folder):
                logging.error(f"Incorrect test setup!  Folder should be non-existent {folder}")

        for file in fail_files:
            if os.path.isfile(file):
                logging.error(f"Incorrect test setup!  File should be non-existent {file}")


    def tearDown(self):
        pass


    def __expand(self, path):
        return os.path.realpath(path)


    def process(self, fail_on_missing=False):
        return pymanifest.process(self.include, self.exclude, fail_on_missing)


    def test_includeFile(self):
        files = set([self.FILE_TXT])
        self.include.files.update(files)
        ret_set = self.process()
        self.assertEqual(files, ret_set)


    def test_includeFiles(self):
        files = set([self.FILE_TXT, self.FILE_EXT])
        self.include.files.update(files)
        ret_set = self.process()
        self.assertEqual(files, ret_set)


    def test_includeNonExistentFile(self):
        files = set([self.FILE_NO])
        self.include.files.update(files)
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_includeNonExistentFiles(self):
        files = set([self.FILE_NO, self.FILE_NO2])
        self.include.files.update(files)
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_excludeExistingFile(self):
        self.include.directories.add(self.TEST_DATA)
        self.exclude.files.add(self.FILE_TXT)

        ret_set = self.process()

        self.assertEqual(ret_set, set([self.FILE_EXT]))


    def test_excludeNonExistingFile(self):
        self.include.directories.add(self.TEST_DATA)
        self.exclude.files.add(self.FILE_NO)

        ret_set = self.process()

        self.assertEqual(ret_set, set([self.FILE_EXT, self.FILE_TXT]))


    def test_includeNonExistingFolder(self):
        self.include.directories.add(self.FOLDER_NO)
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_includeNonExistingFolders(self):
        self.include.directories.update([self.FOLDER_NO, self.FOLDER_NO2])
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_includeNonExistingRecurseFolder(self):
        self.include.recurse_directories.add(self.FOLDER_NO)
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_includeNonExistingRecurseFolders(self):
        self.include.recurse_directories.update([self.FOLDER_NO, self.FOLDER_NO2])
        ret_set = self.process()
        self.assertEqual(ret_set, set())


    def test_recurseDirectory(self):
        self.include.recurse_directories.add(self.SUB_FOLDER)
        ret_set = self.process()

        self.assertEqual(
            ret_set,
            set([
                self.SUB_FOLDER_FILE_TEST,
                self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT
            ])
        )


    def test_recurseDirectoryAndPattern(self):
        self.include.recurse_directories.add(self.SUB_FOLDER)
        self.include.patterns.add('*.txt')
        ret_set = self.process()

        self.assertEqual(ret_set, set([self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT]))


    def test_recurseDirectoryAndExcludePattern(self):
        self.include.recurse_directories.add(self.SUB_FOLDER)
        self.exclude.patterns.add('*.txt')
        ret_set = self.process()

        self.assertEqual(ret_set, set([self.SUB_FOLDER_FILE_TEST]))


    def test_recurseDirectoryAndIncludeExcludePattern(self):
        self.include.recurse_directories.add(self.SUB_FOLDER)
        self.include.patterns.add('*.test')
        self.exclude.patterns.add('*.txt')
        ret_set = self.process()

        self.assertEqual(ret_set, set([self.SUB_FOLDER_FILE_TEST]))


    def test_recurseDirectoryAndExcludePatternToEmpty(self):
        self.include.recurse_directories.add(self.SUB_FOLDER)
        self.exclude.patterns.add('*.test')
        self.exclude.patterns.add('*.txt')
        ret_set = self.process()

        self.assertEqual(ret_set, set())


    def test_recurseDirectoryAndExcludeDirectory(self):
        self.include.recurse_directories.add(self.TEST_DATA)
        self.exclude.directories.add(self.FOLDER_SUB)
        ret_set = self.process()

        self.assertEqual(
            ret_set,
            set([
                self.FILE_EXT,
                self.FILE_TXT,
                self.SUB_FOLDER_FILE_TEST,
                self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT,
            ])
        )


    def test_recurseDirectoryAndExcludeDirectory(self):
        self.include.recurse_directories.add(self.TEST_DATA)
        self.exclude.directories.add(self.FOLDER_SUB)
        ret_set = self.process()

        self.assertEqual(
            ret_set,
            set([
                self.FILE_EXT,
                self.FILE_TXT,
                self.SUB_FOLDER_FILE_TEST,
                self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT,
            ])
        )


    def test_manifest(self):
        self.include.manifests.add(self.INCLUDE_MANIFEST)
        ret_set = self.process()
        self.assertEqual(ret_set, set([
            self.FOLDER_SUB_TEST_FILE,
            self.FOLDER_SUB_WEIRDFILE,
            self.FILE_TXT
        ]))


    def test_recurseDirectoryAndExcludeManifest(self):
        self.include.recurse_directories.add(self.TEST_DATA)
        self.exclude.manifests.add(self.EXCLUDE_MANIFEST)
        ret_set = self.process()
        self.assertEqual(ret_set, set([
            self.FOLDER_SUB_TEST_FILE,
            self.FOLDER_SUB_WEIRDFILE,
            self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT,
            self.SUB_FOLDER_FILE_TEST,
            self.FILE_TXT,
            self.FILE_EXT
        ]))


    def test_recurseDirectoryAndExcludeManifestAndIncludePattern(self):
        self.include.recurse_directories.add(self.TEST_DATA)
        self.include.patterns.add("*.txt")
        self.exclude.manifests.add(self.EXCLUDE_MANIFEST)
        ret_set = self.process()
        self.assertEqual(ret_set, set([
            self.SUB_FOLDER_SUB_SUB_FOLDER_ANOTHERFILE_TXT,
            self.FILE_TXT,
        ]))


if __name__ == '__main__':
    unittest.main()

