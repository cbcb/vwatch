import logging
import re
from requests import get
from typing import List


class Provider:
    @classmethod
    def can_handle(cls, url: str) -> bool:
        '''Return True iff the class can handle url'''
        raise NotImplementedError

    @classmethod
    def get_repo_info(cls, url: str) -> dict:
        '''
        Return repo information for the URL with the fields:
        url             canonical url
        name       canonical (full) name (e.g. "octocat/helloworld" on github)
        description     description
        '''
        raise NotImplementedError

    @classmethod
    def get_releases(cls, name) -> List[dict]:
        '''
        Return release information as a list. Fields for each release:
        name        release name (often like "v1.2.3")
        url         url to the release if applicable
        date        release date (must be compatible with datetime.fromisoformat())
        description description of the release (if any)
        '''
        raise NotImplementedError


# GITHUB #######################################################################
GH_API = 'https://api.github.com'
GH_HEADERS = {
    'User-Agent': 'version-watcher/0.0.1',
    'Accept': 'application/vnd.github.v3+json',
    }


class GithubReleases(Provider):
    name = "GithubReleases"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        '''Return True iff the class can handle url'''
        p = re.compile(r"(https:\/\/)?github.com\/(?P<name>[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)(\/.+)?")
        match = p.match(url)
        if match is None:
            return False
        # See if there are actually releases
        name = match['name']
        response = get(f'{GH_API}/repos/{name}/releases', headers=GH_HEADERS)
        if not response.ok:
            logging.error(f'Github API, {response.url}: {response.status_code}, {response.reason}')
            return
        return len(response.json()) > 0

    @classmethod
    def get_repo_info(cls, url: str) -> dict:
        '''
        Return repo information for the URL with the fields:
        url             canonical url
        name       canonical full name (e.g. "octocat/helloworld" on github)
        description     description
        '''
        p = re.compile(r"(https:\/\/)?github.com\/(?P<name>[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)(\/.+)?")
        name = p.match(url)['name']
        response = get(f'{GH_API}/repos/{name}', headers=GH_HEADERS)
        if not response.ok:
            logging.error(f'Github API, {response.url}: {response.status_code}, {response.reason}')
            return
        description = response.json()['description']
        return {
            'url': f'https://github.com/{name}',
            'name': name,
            'description': description,
        }

    @classmethod
    def get_releases(cls, name) -> List[dict]:
        '''
        Return release information as a list. Fields for each release:
        name        release name (often like "v1.2.3")
        date        release date (must be compatible with datetime.fromisoformat())
        description description of the release (if any)
        '''
        response = get(f'{GH_API}/repos/{name}/releases', headers=GH_HEADERS)
        if not response.ok:
            logging.error(f'Github API, {response.url}: {response.status_code}, {response.reason}')
            return
        releases = []
        for entry in response.json():
            releases.append({
                'name': entry['tag_name'],
                'url': entry['html_url'],
                'date': entry['published_at'].removesuffix("Z"),
                'description': entry['body'],
            })
        return releases


class GithubTags(Provider):
    name = "GithubTags"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        '''Return True iff the class can handle url'''
        p = re.compile(r"(https:\/\/)?github.com\/(?P<name>[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)(\/.+)?")
        match = p.match(url)
        if match is None:
            return False
        # See if there are actually tags
        name = match['name']
        response = get(f'{GH_API}/repos/{name}/tags', headers=GH_HEADERS)
        if not response.ok:
            logging.error(f'Github API, {response.url}: {response.status_code}, {response.reason}')
            return
        return len(response.json()) > 0

    @classmethod
    def get_repo_info(cls, url: str) -> dict:
        # No differences here
        return GithubReleases.get_repo_info(url)

    @classmethod
    def get_releases(cls, name) -> List[dict]:
        '''
        Return release information as a list. Fields for each release:
        name        release name (often like "v1.2.3")
        date        release date (must be compatible with datetime.fromisoformat())
        description description of the release (if any)
        '''
        response = get(f'{GH_API}/repos/{name}/tags', headers=GH_HEADERS)
        if not response.ok:
            logging.error(f'Github API, {response.url}: {response.status_code}, {response.reason}')
            return
        releases = []
        for entry in response.json():
            releases.append({
                'name': entry['name'],
                'url': f"https://github.com/{name}/releases/tag/{entry['name']}",
                # 'date': "",
                # 'description': "",
                # TODO: Lookup commit to get date and description
            })
        return releases


providers = [GithubReleases, GithubTags, ]


def get_provider_by_name(name: str):
    for provider in providers:
        if provider.name == name:
            return provider
    logging.error(f"Provider '{name}' not found")
