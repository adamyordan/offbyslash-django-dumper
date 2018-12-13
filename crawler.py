import requests
import os
from helper import mkdirp, escape_url
import module_inferer

requests.packages.urllib3.disable_warnings()


class Cacher:
    NONEXIST_FILE_PATH = 'cache__nonexist.txt'

    @staticmethod
    def is_nonexist(file):
        if not os.path.exists(Cacher.NONEXIST_FILE_PATH):
            open(Cacher.NONEXIST_FILE_PATH, 'w').write('')
        nonexist_files = open(Cacher.NONEXIST_FILE_PATH, 'r').read().split('\n')
        return file in nonexist_files

    @staticmethod
    def add_to_nonexist(file):
        open(Cacher.NONEXIST_FILE_PATH, 'a').write(file + '\n')


class Dumper:
    @staticmethod
    def get(url, path):
        file_dst = Dumper._resolve_dump_file_path(url, path)
        if Cacher.is_nonexist(file_dst):
            return None
        elif os.path.exists(file_dst):
            return open(file_dst, 'r').read()
        else:
            content = Dumper.download(url, path)
            if content is None:
                Cacher.add_to_nonexist(file_dst)
            return content


    @staticmethod
    def download(url, path):
        file_dst = Dumper._resolve_dump_file_path(url, path)
        if os.path.exists(file_dst):
            return

        url = '{0}static../{1}'.format(url, path)
        res = requests.get(url, verify=False)

        if res.status_code == 200 and res.text:
            print('[+] downloading: {}'.format(file_dst))
            mkdirp(os.path.dirname(file_dst))
            open(file_dst, 'w').write(res.text.encode('utf8'))
            return res.text
        else:
            return None


    @staticmethod
    def _resolve_dump_file_path(url, path):
        return 'dump/{0}/{1}'.format(escape_url(url), path)


class Parser:
    @staticmethod
    def parse_main_module(manage_py_content):
        return manage_py_content.split('''os.environ.setdefault("DJANGO_SETTINGS_MODULE"''')[1].split('"')[1][:-len('settings') - 1]

    @staticmethod
    def parse_installed_apps(settings_content):
        if not settings_content:
            return None
        bracket = ']' if '[' in settings_content.split('INSTALLED_APPS')[1].split('\n')[0] else ')'
        x = settings_content.split('INSTALLED_APPS')[1].split(bracket)[0].split('\n')
        y = []
        for app in x:
            if "'" in app or '"' in app:
                if 'django' not in app:
                    app = app.split('#')[0].strip()
                    y.append(app.strip().replace('"', '').replace("'", '').replace(',', ''))
        return y


class Crawler:
    COMMON_FILES = ['manage.py', 'config.py', 'views.py', 'views/__init__.py']
    COMMON_FILES_IN_MODULE = ['__init__.py', 'settings.py', 'urls.py', 'wsgi.py',
                              'admin.py', 'apps.py', 'helper.py', 'models.py', 'tasks.py',
                              'tests.py', 'views.py', 'migrations/0001_initial.py', 'migrations/__init__.py']

    @staticmethod
    def _module_name_to_path(m):
        return m.replace('.', '/')

    @staticmethod
    def _get_module_name_from_path(path):
        structures = path.split('/')
        return '.'.join(structures[:-1])

    @staticmethod
    def _crawl_expand(url, initial_files):
        candidate_files = set(initial_files)
        checked_files = set()

        while True:
            if checked_files == candidate_files:
                break

            new_files = set()
            for f in candidate_files:
                if f in checked_files:
                    continue
                checked_files.add(f)
                content = Dumper.get(url, f)
                if not content:
                    continue
                module_name = Crawler._get_module_name_from_path(f)
                inferred_modules = module_inferer.find_modules_in_script(content, module_name)
                for m in inferred_modules:
                    mp = Crawler._module_name_to_path(m)
                    new_files.add('{}.py'.format(mp))
                    new_files.update(['{}/{}'.format(mp, c) for c in Crawler.COMMON_FILES_IN_MODULE])

            candidate_files.update(new_files)

    @staticmethod
    def crawl(url):
        print '[+] START CRAWLING: ' + url
        candidate_files = set(Crawler.COMMON_FILES)

        content_manage_py = Dumper.get(url, 'manage.py')
        main_module = Parser.parse_main_module(content_manage_py)
        main_module_path = Crawler._module_name_to_path(main_module)

        content_settings_py = Dumper.get(url, '{}/settings.py'.format(main_module_path))
        app_modules = Parser.parse_installed_apps(content_settings_py)

        for m in app_modules + [main_module]:
            mp = Crawler._module_name_to_path(m)
            candidate_files.add('{}.py'.format(mp))
            candidate_files.update(['{}/{}'.format(mp, c) for c in Crawler.COMMON_FILES_IN_MODULE])

        Crawler._crawl_expand(url, initial_files=candidate_files)

        print '[+] FINISHED: ' + url
