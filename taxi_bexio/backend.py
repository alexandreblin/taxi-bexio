from collections import defaultdict

from taxi.aliases import aliases_database
from taxi.backends import BaseBackend, PushEntryFailed
from taxi.projects import Activity, Project

import requests
import datetime


class BexioBackend(BaseBackend):
    def __init__(self, **kwargs):
        super(BexioBackend, self).__init__(**kwargs)

        self.name = 'bexio'
        self.path = self.path.lstrip('/')
        self.settings = self.context['settings']

        self.instance = kwargs['username']
        self.api_key = kwargs['password']
        self.hostname = kwargs['hostname']
        self.user_id = int(kwargs['options']['user'])
        self.client_service_id = int(kwargs['options']['client_service'])
        self.timesheet_status_id = int(kwargs['options']['timesheet_status'])

    def push_entry(self, date, entry):
        m, s = divmod(int(entry.hours * 3600), 60)
        h, m = divmod(m, 60)
        duration = f"{h:02d}:{m:02d}"

        mapping = aliases_database[entry.alias]
        project_id = int(mapping.mapping[1])

        r = requests.get(
            f"https://{self.hostname}/2.0/pr_project/{project_id}",
            headers={'Accept': 'application/json', 'Authorization': f"Bearer {self.api_key}"}
        )
        response = r.json()
        contact_id = None
        contact_sub_id = None

        if r.status_code == 200:
            contact_id = int(response['contact_id'])
            contact_sub_id = int(response['contact_sub_id'])

        r = requests.post(
            f"https://{self.hostname}/2.0/timesheet",
            json={
                'user_id': self.user_id,
                'status_id': self.timesheet_status_id,
                'client_service_id': self.client_service_id,
                'text': entry.description,
                'allowable_bill': True,
                'contact_id': contact_id,
                'sub_contact_id': contact_sub_id,
                'pr_project_id': project_id,
                'tracking': {
                    'type': 'duration',
                    'date': date.strftime('%Y-%m-%d'),
                    'duration': duration
                }
            },
            headers={'Accept': 'application/json', 'Authorization': f"Bearer {self.api_key}"}
        )
        response = r.json()

        if r.status_code != 201:
            raise PushEntryFailed(f"[{self.name}] API error: HTTP {r.status_code} - {response['message']}")

    def get_projects(self):
        projects_list = []

        p = Project(self.instance.upper(), f"[{self.name}] {self.instance}", Project.STATUS_ACTIVE,
                    description=f"{self.name} Project {self.instance}"
                    )

        r = requests.get(
            f"https://{self.hostname}/2.0/pr_project",
            headers={'Accept': 'application/json', 'Authorization': f"Bearer {self.api_key}"}
        )
        response = r.json()

        if r.status_code != 200:
            raise Exception(f"[{self.name}] API error: HTTP {r.status_code} - {response['message']}")

        for project in response:
            name = f"{self.instance.upper()}-{project['id']}"

            # @todo Ideally, we should have a [bexio_active_project_states] configuration that lists only active
            # projects and filter here again against /2.0/pr_project_state
            if project['end_date'] is not None:
                if datetime.datetime.strptime(project['end_date'], '%Y-%m-%d %H:%M:%S') < datetime.datetime.today():
                    continue

            a = Activity(project['id'], project['name'])
            p.add_activity(a)
            p.aliases[name] = a.id

        projects_list.append(p)

        return projects_list
