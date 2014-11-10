from fabric.api import cd, env, lcd, put, local, run, sudo, prefix
from fabric.contrib.files import exists


PROJECT_NAME = 'savory'

LOCAL_CONFIG_DIR = './config'

REMOTE_APP_DIR = '/home/perlence'
REMOTE_PACKAGE_DIR = '/home/perlence/savory'

env.hosts = ['104.219.53.106']
env.user = 'perlence'
env.colorize_errors = True


def install_requirements():
    """Install required packages."""
    sudo('apt-get update')
    sudo('apt-get install -y python')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y nginx')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y git')
    sudo('apt-get install -y redis-server')
    sudo('apt-get install -y mongodb-server')
    sudo('apt-get install -y nodejs-legacy')
    sudo('apt-get install -y npm')
    sudo('apt-get install -y ruby')
    sudo('apt-get install -y gem')

    sudo('pip install virtualenv')
    sudo('pip install gunicorn')

    sudo('npm install bower')
    sudo('npm install coffee-script')
    sudo('npm install autoprefixer')

    sudo('gem install sass')


def configure_environment():
    """Configure virtual environment.

    1. Create project directories
    2. Create and activate a virtualenv
    """
    if not exists(REMOTE_PACKAGE_DIR):
        run('mkdir -p ' + REMOTE_PACKAGE_DIR)
    with cd(REMOTE_PACKAGE_DIR):
        run('virtualenv env')


def configure_nginx():
    """Configure nginx.

    1. Remove default nginx config file
    2. Create new config file
    3. Setup new symbolic link
    4. Copy local config to remote config
    5. Restart nginx
    """
    logs = REMOTE_PACKAGE_DIR + '/logs'
    if not exists(logs):
        run('mkdir ' + logs)
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm /etc/nginx/sites-enabled/default')
    if not exists('/etc/nginx/sites-enabled/' + PROJECT_NAME):
        sudo('touch /etc/nginx/sites-available/' + PROJECT_NAME)
        sudo('ln -s /etc/nginx/sites-available/{PROJECT_NAME}'
             ' /etc/nginx/sites-enabled/{PROJECT_NAME}'
             .format(PROJECT_NAME=PROJECT_NAME))
    with lcd(LOCAL_CONFIG_DIR):
        with cd('/etc/nginx/sites-available'):
            put('nginx.conf', PROJECT_NAME, use_sudo=True)
    sudo('service nginx restart')


def supervisorctl(command=''):
    """Access remote supervisorctl."""
    sudo('supervisorctl -c /etc/supervisor/supervisord.conf ' + command)


def configure_supervisor():
    """Configure Supervisor.

    1. Create new supervisor config file
    2. Copy local config to remote config
    3. Register new command
    """
    logs = REMOTE_PACKAGE_DIR + '/logs'
    if not exists(logs):
        run('mkdir ' + logs)
    with lcd(LOCAL_CONFIG_DIR):
        with cd('/etc/supervisor/conf.d'):
            put('supervisord.conf', PROJECT_NAME + '.conf', use_sudo=True)
            supervisorctl('reread')
            supervisorctl('update')


def configure_git():
    """Configure git.

    1. Setup bare Git repo
    2. Create post-receive hook
    """
    with cd(REMOTE_APP_DIR):
        run('mkdir ' + PROJECT_NAME + '.git')
        with cd(PROJECT_NAME + '.git'):
            run('git init --bare')
            with lcd(LOCAL_CONFIG_DIR):
                with cd('hooks'):
                    put('post-receive', './')
                    run('chmod +x post-receive')


def run_app():
    """Run the app!"""
    supervisorctl('start ' + PROJECT_NAME)


def deploy():
    """Deploy the project.

    1. Copy new Flask files
    2. Restart gunicorn via supervisor
    """
    local('git push production master')
    with cd(REMOTE_PACKAGE_DIR):
        with prefix('source env/bin/activate'):
            run('pip install --force-reinstall -r requirements.txt')
            run('python setup.py develop')
        # Install Bower dependencies for Elaborate Last.fm Charts.
        with cd('env/src/elaborate-lastfm-charts'):
            run('bower install')
    supervisorctl('restart ' + PROJECT_NAME)


def status():
    """Check if our app is live."""
    sudo('service nginx status')
    supervisorctl('status')


def init():
    """Install requirements and configure git, nginx, and supervisor."""
    install_requirements()
    configure_environment()
    configure_git()
    configure_nginx()
    configure_supervisor()
