class JiraIssue:
    projects = {}

    def __init__(self, uri=None, key=None):
        self.issue_uri = uri
        self.issue_key = key
        self.project_key = None
        self.project_id = None

    @staticmethod
    def parse(json_object):
        ticket = JiraIssue()
        ticket.issue_uri = json_object["self"]
        ticket.issue_key = json_object["key"]

        dot_index = ticket.issue_key.find('-')
        ticket.project_key = ticket.issue_key[:dot_index]

        return ticket
