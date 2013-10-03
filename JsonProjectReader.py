import json

__author__ = 'bartek'


class ProjectParser(object):
    def parse(self):
        raise NotImplementedError()

class JSONParsingError(Exception):
    pass


class MultimodeParser(ProjectParser):
    def __init__(self, jsonDictionary):
        pass

    def parse(self):
        pass

class SinglemodeParser(ProjectParser):
    def __init__(self, jsonDictionary):
        pass

    def parse(self):
        pass


class JSONProjectReader(object):
    PROBLEM_TYPE_TAG = "problem_type"
    PROBLEM_TAG ="problem"
    MUTLIMODE_PROBLEM_TYPE = "multimode"
    SINGLE_MODE_PROBLEM_TYPE = "singlemode"


    def read(self, filename):
        """

        :param filename: absolute path to json file containing project description
        :return: Project instance described in json file
        :rtype:
        """
        with open(filename) as file:
            content = file.readall()
            self._rawJSONContent = json.loads(content)
            parser = self.retrieveType()
            return parser.parse()

    def retrieveType(self):
        problem_type = self._rawJSONContent[self.PROBLEM_TYPE_TAG]
        if problem_type == self.MUTLIMODE_PROBLEM_TYPE:
            return MultimodeParser(self._rawJSONContent[self.PROBLEM_TAG])
        elif problem_type == self.SINGLE_MODE_PROBLEM_TYPE:
            return SinglemodeParser(self._rawJSONContent[self.PROBLEM_TAG])
        else:
            raise JSONParsingError("Cannot find parser for given type")
        #TODO: end writing JSON project reader and test it




