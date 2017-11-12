import sys
import os
import json
import datetime
import random
import click
from jinja2 import Template
from collections import named_tuple


Problem = named_tuple('Problem', ['id_', 'url', 'samples'])


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
    return open(os.path.join('language_templates', language, 'extension.txt')).read()

def get_random_problem():
    problems = json.load(open('problems.json'))
    problem_dict = random.choice(problems)

    return Problem(problem_dict['id'], problem_dict['url'], problem_dict['samples'])


def get_template_string(language):
    try:
        return open(os.path.join('language_templates', language, 'source.j2')).read()
    except IOError:
        print('language template is not found')
        sys.exit(-1)


def create_scaffold_for_solve(problem, source, extension, now):
    base_dir = os.path.join('.', now, problem.id_)
    os.makedirs(base_dir)

    filename = os.path.join(base_dir, 'prog.{}'.format(extension))
    print('created {}'.format(filename))
    open(filename, 'w').write(source)
    filename = os.path.join(base_dir, 'in.txt', 'w')
    print('created {}'.format(filename))
    open(filename).write(problem.samples['in'])
    filename = os.path.join(base_dir, 'out.txt', 'w')
    print('created {}'.format(filename))
    open(filename).write(problem.samples['out'])


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command()
@click.option('language', 'l')
def fetch_problem(language):
    language = get_default_language() if language is None else language
    problem = get_random_problem()

    template_string = get_template_string(language)
    template = Template(template_string)

    now = datetime.datetime.now().strftime('%Y%m%d')

    source = template.render(**{
        'now': now,
        'problem': problem
    })

    create_scaffold_for_solve(problem, source, get_language_extension(language), now)
