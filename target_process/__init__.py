import json
import colors
from client import TargetProcessClient


class TargetProcess:
    def __init__(self, token):
        self.token = token
        self.user_stories = {}

        if self.token is None:
            print colors.error("Token cant be empty")
            exit()
        else:
            self.tp = TargetProcessClient(self.token)

    def set_user_stories_ids(self, user_stories_ids):
        if not isinstance(user_stories_ids, list):
            print colors.error("User stories should be list instance")
            exit()

        response = self.tp.get('UserStories', {'id': user_stories_ids})

        if response.status_code != 200:
            print colors.error("Cant get user stories")
            exit()

        self.user_stories = json.loads(response.text)

        if 'Items' not in self.user_stories:
            print colors.error('Bad response')
            exit()

    def check_user_stories(self):
        if self.user_stories == {}:
            raise ValueError('User stories must be set')

    def change_state_add_tag(self, to_state, tag):
        self.check_user_stories()
        succeed = []
        failed = []
        for user_story in self.user_stories['Items']:
            response = self.tp.post('UserStories', {
                'Id': user_story['Id'],
                'EntityState': {'Id': self.tp.getStateCode(to_state)},
                'Tags': user_story['Tags'] + ', ' + tag
            })

            if response.status_code == 200:
                succeed.append(
                    "User story %d \"%s\" -> \"%s\" add tag %s" %
                    (user_story['Id'], user_story['EntityState']['Name'], to_state, tag)
                )
            else:
                failed.append("User story %d udpate failed" % user_story['Id'])

        return succeed, failed

    def move_user_stories(self, to_state):
        self.check_user_stories()
        succeed = []
        failed = []
        for user_story in self.user_stories['Items']:
            response = self.tp.post('UserStories', {
                'Id': user_story['Id'],
                'EntityState': {'Id': self.tp.getStateCode(to_state)}
            })

            if response.status_code == 200:
                succeed.append(colors.success("User story {} \"{}\" -> \"{}\" success".format(
                    user_story['Id'],
                    user_story['EntityState']['Name'],
                    to_state
                )))
            else:
                failed.append(colors.error("User story {} \"{}\" -> \"{}\" failed".format(
                    user_story['Id'],
                    user_story['EntityState']['Name'],
                    to_state
                )))

        return succeed, failed

    def add_tag(self, tag):
        self.check_user_stories()
        succeed = []
        failed = []

        for user_story in self.user_stories['Items']:
            response = self.tp.post('UserStories', {
                'Id': user_story['Id'],
                'Tags': user_story['Tags'] + ', ' + tag
            })

            if response.status_code == 200:
                succeed.append(colors.success("User story %d add tag '%s' success" % (user_story['Id'], tag)))
            else:
                failed.append(colors.error("User story %d add tag '%s' failed" % (user_story['Id'], tag)))

        return succeed, failed
