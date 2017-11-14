import sys
import os
import json
import datetime
import random
import subprocess
import click
from jinja2 import Template
from collections import namedtuple


ASSET_DIR = '.'
WORK_DIR = 'workdir'

Problem = namedtuple('Problem', ['id_', 'url', 'in_', 'out_'])


def get_default_language():
    return json.load(open('settings.json'))['language']


def set_default_language(language):
    try:
        d = json.load(open('settings.json'))['language']
    except IOError:
        d = {}
    d['language'] = language
    json.dump(open('settings.json', 'w')).write(d)


def get_language_extension(language):
    return open(os.path.join(ASSET_DIR, 'language_templates', language, 'extension.txt')).read().strip()


def get_random_problem():
    problems_dir = os.path.join(ASSET_DIR, 'problems')
    problems = list(map(lambda x: os.path.join(problems_dir, x), os.listdir(problems_dir)))
    problem_dir = random.choice(problems)
    problem_information = json.load(open(os.path.join(problem_dir, 'information.json')))

    return Problem(
        id_=problem_information['id'], url=problem_information['url'],
        in_=open(os.path.join(problem_dir, 'in.txt')).read(),
        out_=open((os.path.join(problem_dir, 'out.txt'))).read()
    )


def get_template_string(language):
    try:
        return open(os.path.join(ASSET_DIR, 'language_templates', language, 'source.j2')).read()
    except IOError:
        print('language template is not found')
        sys.exit(-1)


def create_scaffold_for_solve(problem, source, extension, now):
    base_dir = os.path.join(WORK_DIR, now, problem.id_)
    os.makedirs(base_dir)

    filename = os.path.join(base_dir, 'prog.{}'.format(extension))
    print('created {}'.format(filename))
    open(filename, 'w').write(source)
    filename = os.path.join(base_dir, 'in.txt')
    print('created {}'.format(filename))
    open(filename, 'w').write(problem.in_)
    filename = os.path.join(base_dir, 'out.txt')
    print('created {}'.format(filename))
    open(filename, 'w').write(problem.out_)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command(help="test")
def fetch_problem():
    language = get_default_language()
    problem = get_random_problem()

    template_string = get_template_string(language)
    template = Template(template_string)

    now = datetime.datetime.now().strftime('%Y%m%d')

    source = template.render(**{
        'now': now,
        'problem': problem
    })

    create_scaffold_for_solve(problem, source, get_language_extension(language), now)
    print('open {}'.format(problem.url))
    os.system('open "{}"'.format(problem.url))


@cli.command(help="sample check")
@click.option("--target", '-t')
def check_sample(target):
    language = get_default_language()
    run_sh = os.path.join('language_templates', language, 'run.sh')

    proc = subprocess.run(["sh", run_sh,
        os.path.join(target, 'prog.{}'.format(get_language_extension(language))),
        os.path.join(target, 'in.txt'),
    ], stdout=subprocess.PIPE)

    out = proc.stdout.decode('ascii')
    sample = open(os.path.join(target, 'out.txt')).read()

    if out == sample:
        print('Accept')
    else:
        print('Wrong Anser')
        print('output')
        print(out)
        print('-' * 20)
        print('sample')
        print(sample)


@cli.command(help="create problem")
@click.argument('id')
@click.argument('url')
def create_problem(id, url):
    os.makedirs(os.path.join(ASSET_DIR, 'problems', 'problem_{}'.format(id)))
    os.system('touch {}'.format(os.path.join(ASSET_DIR, 'problems', 'problem_{}'.format(id), 'in.txt')))
    os.system('touch {}'.format(os.path.join(ASSET_DIR, 'problems', 'problem_{}'.format(id), 'out.txt')))

    json.dump({
        "id": id,
        "url": url,
    }, open(os.path.join(ASSET_DIR, 'problems', 'problem_{}'.format(id), 'information.json'), 'w'))


if __name__ == '__main__':
    cli()
