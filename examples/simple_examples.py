"""
Basic usage examples

Most of this usage follows a pattern of first extracting a list of matching
elements, say 'project' or 'story' and then processing that list by using
the .find method to extract specific attributes of the items.

View the response examples in the Pivotal API docs to see the elements
available in the responses.
"""
import sys
from os.path import expanduser

from pivotal import Pivotal
from pivotal.anyetree import etree


# Config
pivotal_token = ''
token_file = '~/.pivotal_token'
endpoint = 'http://www.pivotaltracker.com/services/v3/'
PIVOTAL_USER = 'Al Swearingen' # valid member of a Pivotal project
# EndConfig

token_path = expanduser(token_file)

if not pivotal_token:
    try:
        pivotal_token = file(token_path).readlines()[0]
    except:
        sys.exit('Pivotal Tracker token not specified.\n \
            Add to the script or create in ~/.pivotal_token')

boolmap = {
    'true': True,
    'false': False
}

pv = Pivotal(pivotal_token)

##############################################################################
# Find all projects and create a dictionary of basic project info
##############################################################################
projects = {}
project_choices = []

_projects = pv.projects().get_etree().findall('project')
for pos, project in enumerate(_projects):
    pid = project.find('id').text
    pname = project.find('name').text
    use_https = boolmap[project.find('use_https').text]
    labels = project.find('labels').text.split(',')
    projects[pos+1] = {
        'id': pid,
        'name': pname,
        'use_https': use_https,
        'labels': labels
        }
    project_choices.append('[%d] %s' % (pos+1, pname))

project_choices.append('[Q(uit)] to Quit')



##############################################################################
# USER INPUT to choose a project from the available list
##############################################################################
print "Pivotal Tracker Projects"
choice = ''

valid_choices = [str(i) for i in projects.keys() + ['q','Q']]

while choice not in valid_choices:
    print '\n'.join(project_choices)
    choice = raw_input('Choose a Project #: ')

if choice in ['q', 'Q']:
    sys.exit()

project = projects[int(choice)]
# Some projects require https, if so, set it on the Pivotal instance
pv.use_https = project['use_https']




##############################################################################
# Find all unstarted Stories for this project, create a dictionary keyed by id
##############################################################################
_stories = pv.projects(project['id']).stories(filter='state:unstarted').get_etree()

print "%s has %d Stories to be started" % (project['name'], len(_stories))

stories = {}
story_choices = []

for pos, story in enumerate(_stories):
    id = story.find('id').text
    name = story.find('name').text
    description = story.find('description').text
    _labels = story.find('labels')
    labels = []
    if _labels is not None:
        labels = _labels.text.split(',')
    stories[id] = dict(name = name,
                       description = description,
                       labels = labels,
                       )

    # Display up to the first 5 stories
    if pos < 5:
        print "#%s: %s (%d labels)" % (id, name, len(labels))
    elif pos == 5:
        print "(%d more...)\n" % (len(_stories) - 5)

    


##############################################################################
# Add a new story using POST
##############################################################################
new_story = pv.projects(project['id']).stories().add('story',
           name='A hooplehead should be able to get his drink on at The Gem',
           description='Bar should be full and plenty',
           requested_by=PIVOTAL_USER)

# Response contains the http response
# Content contains the xml string
response, content = new_story.post()

if response['status'] != '200':
    print "There was an error adding the story"
    print 'Status Code: %s' % response['status']
    for error in content.findall('error'):
        print error.text
    sys.exit('Bye!')


_story = etree.fromstring(content)
story_id = _story.find('id').text
print "Added new story #%s" % story_id



##############################################################################
# Update the story using PUT
##############################################################################
story = pv.projects(project['id']).stories(story_id).update('story',
            description='Bar should have plenty of whiskey')
response, content = story.put()

if response['status'] == '200':
    print "Story #%s updated successfully" % story_id
else:
    
    print "There was an error updating the story"
    print 'Status Code: %s' % response['status']
    for error in content.findall('error'):
        print error.text
    sys.exit('Bye!')



##############################################################################
# Add a Task using POST
##############################################################################
new_task = pv.projects(project['id']).stories(story_id).tasks().add('task',
            description='Wake up the bartender')
response, content = new_task.post()
if response['status'] != '200':
    print "There was an error adding the task"
    print 'Status Code: %s' % response['status']
    for error in content.findall('error'):
        print error.text
    sys.exit('Bye!')


_task = etree.fromstring(content)
task_id = _task.find('id').text
print "Added new Task #%s to Story #%s" % (task_id, story_id)


##############################################################################
# Update the task using PUT
##############################################################################
task = pv.projects(project['id']).stories(story_id).tasks(task_id).update('task',
            description='Bar should have plenty of whiskey and rum')
response, content = task.put()

if response['status'] == '200':
    print "Task #%s updated successfully" % task_id
else:
    
    print "There was an error updating the Task"
    print 'Status Code: %s' % response['status']
    for error in content.findall('error'):
        print error.text
    sys.exit('Bye!')
