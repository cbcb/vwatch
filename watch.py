#!/usr/bin/env python3

from datetime import datetime
import logging
import json
import os
import sys

from provider import providers, get_provider_by_name
import output as out


SHOW_N_NEWEST = 25  # max. number of releases to show
DATA_FILE = "data/data.json"  # data is saved here


def main():
    argc = len(sys.argv)
    if argc == 1:
        watch()
    elif sys.argv[1] in ['-h', '--help']:
        print_help()
    elif sys.argv[1] == 'add':
        for url in sys.argv[2:]:
            add(url)
    elif argc == 2 and sys.argv[1] == 'watch':
        watch()
    else:
        print('Could not parse command line.')
        print_help()


def add(url):
    print(f"Trying to add {url}…")
    added = False
    for provider in providers:
        if not provider.can_handle(url):
            continue
        repo = provider.get_repo_info(url)
        print(f"Found {out.repo(repo['name'])} at {repo['url']}")
        print(f"Description: {out.desc(repo['description'])}")
        print()
        release = ask_release(provider.get_releases(repo['name']))
        if release is None:
            continue
        record(repo, provider.name, release)
        added = True
        break
    if not added:
        print(f"Could not add {url}.")


def ask_release(releases):
    for i in range(min(len(releases), SHOW_N_NEWEST)):
        print(f"{out.bracketed(i)} {releases[i]['name']}")
    while True:
        choice = input("enter number of your release [0]: ")
        if choice == '':
            return releases[0]
        try:
            return releases[int(choice)]
        except Exception:
            continue


def record(repo, provider_name, release):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            file.write("{}")
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
        data[repo['name']] = {
            'url': repo['url'],
            'description': repo['description'],
            'release': release['name'],
            'provider': provider_name,
        }
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Recorded {out.repo(repo['name'])}-{out.ver(release['name'])}")


def watch():
    if not os.path.exists(DATA_FILE):
        logging.error("Data file does not exist. Try <add> first?")
        sys.exit(1)
    releases = {}
    while(True):
        print('Listing recorded packages:\n')
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
        repos = list(data.keys())
        for i in range(len(data)):
            reponame = repos[i]
            if reponame not in releases:
                provider = get_provider_by_name(data[reponame]['provider'])
                releases[reponame] = provider.get_releases(reponame)
            print_release_line(i, reponame, data[reponame]['release'], releases[reponame][0]['name'])
        print()
        id = input("Enter row number to show and mark updated (or nothing to quit): ")
        if id.lower() in ["", "q", "quit", "exit"]:
            break
        try:
            id = int(id)
            if id >= len(repos) or id < 0:
                continue
        except Exception:
            continue
        repo = repos[id]
        edit(repo, data[repo], releases[repo])


def print_release_line(i, repo_name, old_tag, new_tag):
    if old_tag == new_tag:
        spec = out.good(f'{old_tag} ✓')
    else:
        spec = out.bad(old_tag, new_tag)
    print(f'| {i:2} | {out.repo(repo_name):>40} |', spec)


def edit(repo_name, repo_data, releases):
    print()
    print("="*100)
    print(f"Repo: {out.repo(repo_name)}")
    print(f"Desc: {out.desc(repo_data['description'])}")
    print(f"URL: {out.url(repo_data['url'])}")
    print("="*100)
    print()
    counter = 0
    tags = []
    for release in releases:
        print('-'*80)
        tag = release['name']
        tags.append(tag)
        url = release['url']
        current = repo_data['release']
        if tag == current:
            print(f'Current: {out.bold(tag):15} {url}')
        elif counter == 0:
            print(f'{out.bracketed(counter)} {out.good(tag):15} {url}')
        else:
            print(f'{out.bracketed(counter)} {out.ver(tag):15} {url}')
        if 'date' in release:
            print(f"Released {out.bold(humanize_date(release['date']))}")
        if tag == current:
            break
        if 'description' in release:
            print(release['description'])
        print()
        counter += 1
    if counter == 0:
        print()
        print("Nothing to update!")
        input("Press enter to return. ")
        return
    while True:
        print()
        print("Enter number or tag to record update; 'u' to make as updated to newest, or hit enter to return")
        ask = input("? ")
        if ask == "":
            return
        if ask.lower() == "u":
            update(repo_name, tags[0])
            # print(f"Update to {tags[0]}")
            return
        if ask in tags:
            update(repo_name, ask)
            # print(f"Update to {ask}")
            return
        if ask.isnumeric() and 0 <= int(ask) < counter:
            update(repo_name, tags[int(ask)])
            # print(f"Update to {tags[int(ask)]}")
            return
        print("No such tag…")


def update(repo_name, release):
    if not os.path.exists(DATA_FILE):
        logging.error("DATA_FILE disappeared...")
        sys.exit(3)
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
        data[repo_name]['release'] = release
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Marked update to {out.repo(repo_name)}-{out.ver(release)}")


def humanize_date(date: str):
    date = datetime.fromisoformat(date)
    days = (datetime.now() - date).days
    if days < 2:
        return "1 day ago"
    if days <= 14:
        return f"{days} days ago"
    if days <= 6*7:
        return f"{days//7} weeks ago"
    return f"{days//30} months ago"


def print_help():
    print(f"""\
usage: {sys.argv[0]} [-h|--help] [COMMAND]

available commands:
  add
    add URL [URL ...]   for each URL, add the repo it represents to the collection
  watch
    watch               watch tracked repos

watch is the default command if no COMMAND is given.

optional arguments:
  -h, --help    show this help message and exit""")


if __name__ == "__main__":
    main()
