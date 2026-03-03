"""Fabric 2 deployment tasks for Circa-BE (envcoord).

Usage:
    fab update       # pull repos + buildout + rolling restart
    fab restart      # buildout + rolling restart
    fab shutdown     # stop all services
    fab start        # start all services
    fab ssh          # open remote shell
"""

from invoke import task
from fabric import Connection

HOST = 'circa'  # uses SSH config (~/.ssh/config)
REPO = '/var/local/circa-be/buildout'
HAPROXY_CFG = f'{REPO}/haproxy.cfg'

INSTANCES = [
    'envcoord-1',
    'envcoord-2',
    'envcoord-3',
]


def get_conn():
    return Connection(HOST)


@task
def ssh(c):
    """Open a shell on the remote server."""
    get_conn().run(f'cd {REPO} && exec bash -l', pty=True)


@task
def restart(c):
    """Run buildout and perform rolling restart of all Zope instances."""
    conn = get_conn()
    conn.run(f'{REPO}/bin/buildout -c {REPO}/buildout.cfg')
    for instance in INSTANCES:
        conn.run(f'{REPO}/bin/{instance} stop', warn=True)
        conn.run('sleep 0.5')
        conn.run(f'{REPO}/bin/{instance} start')
        conn.run('sleep 5')


@task
def shutdown(c):
    """Stop haproxy, all Zope instances, and ZEO server."""
    conn = get_conn()
    conn.run('kill -9 $(pidof haproxy)', warn=True)
    for instance in INSTANCES:
        conn.run(f'{REPO}/bin/{instance} stop', warn=True)
        conn.run('sleep 0.5')
    conn.run(f'{REPO}/bin/zeoserver stop', warn=True)


@task
def start(c):
    """Start ZEO server, all Zope instances, and haproxy."""
    conn = get_conn()
    conn.run(f'{REPO}/bin/zeoserver start')
    for instance in INSTANCES:
        conn.run(f'{REPO}/bin/{instance} start')
        conn.run('sleep 3')
    conn.run(f'{REPO}/bin/haproxy -D -f {HAPROXY_CFG}')


@task
def update(c):
    """Full update: rebuild and rolling restart."""
    restart(c)
