version watcher
===============
Little utility to watch the version of software.

Supported data sources
======================
* Github releases
* Github tags

Security
========

All user input is trusted. All github API responses are trusted. That includes commit messages. That's not good.

Known problems
==============
* User input is foolishly trusted.
* Github API is accessed without authentication. Unauthenticated access is limited to 60 calls per hour or so.
