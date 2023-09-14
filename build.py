#!/usr/bin/env python3
import argparse
import json
import os
import subprocess

class Config:
    def __init__(self, name):
        self.name = name
        self.bench_class = ''
        self.compiler = ''
        self.comp_options = ''
        self.link_opts = ''
        self.ucompiler = ''
        self.ucomp_options = ''
        self.omp_lib = None
    def add_option(self, config, opt_name, attr_name, required):
        if opt_name in config:
            setattr(self, attr_name, config[opt_name])
        else:
            if required:
                raise Exception('Mandatory {} entry not found in config'.format(opt_name))

def parse_config(config):
    config_json = json.loads(config)
    ret = {}
    for conf_name, conf in config_json.items():
        c = Config(conf_name)
        c.add_option(conf, "class", "bench_class", True)
        c.add_option(conf, "compiler", "compiler", True)
        c.add_option(conf, "compiler_options", "comp_options", False)
        c.add_option(conf, "link_options", "link_opts", False)
        c.add_option(conf, "utility_compiler", "ucompiler", True)
        c.add_option(conf, "utility_compiler_options", "ucomp_options", False)
        c.add_option(conf, "omp_lib", "omp_lib", False)
        ret[conf_name] = c
    return ret

def get_make_command():
    return 'make'

def get_prog_list():
    return ['CG', 'FT', 'EP', 'LU', 'MG', 'SP']

def prepare_build_dir(config):
    if not os.path.isdir('build'):
        os.mkdir('build')
    build_dir = os.path.join('build', '{}'.format(config.name))
    if not os.path.isdir(build_dir):
        os.mkdir(build_dir)
    os.system('rm -rf {}/*'.format(build_dir))
    return 'build'

def get_omp_c_root():
    if not os.path.isdir('omp-c'):
        raise Exception('omp-c is not checked out. Use: git submodule update omp-c')
    return 'omp-c'

def get_omp_config_dir():
    root_dir = get_omp_c_root()
    config_dir = os.path.join(root_dir, 'config')
    if not os.path.isdir(config_dir):
        raise Exception('config directory not present in omp-c')
    return config_dir
def configure_project(config):
    with open("make.def.in", "r") as make_template:
        template_str = make_template.read()
        openmp_flag=' -fopenmp'
        if config.omp_lib is not None:
            openmp_flag +='={}'.format(config.omp_lib)
        config_str = template_str.format(compiler=config.compiler, linked_libs='-lm', 
                additional_macros='', c_flags=config.comp_options + openmp_flag, 
                link_flags=config.link_opts + openmp_flag, suit_name='{}'.format(config.name), u_compiler=config.ucompiler, u_c_flags=config.ucomp_options)
        print(config_str)
        config_dir = get_omp_config_dir()
        config_path = os.path.join(config_dir, 'make.def')
        with open(config_path, "w") as config_file:
            config_file.write(config_str)

def post_build_clean():
    config_path = os.path.join(get_omp_config_dir(), 'make.def')
    os.remove(config_path)

def build_project(config):
    build_dir = prepare_build_dir(config)
    print('Building omp-c using {} configuration'.format(config.name))
    configure_project(config)
    for prog in get_prog_list():
        status = subprocess.run([get_make_command(), prog, "CLASS={}".format(config.bench_class)], capture_output=True, cwd=get_omp_c_root())
        if status.returncode != 0:
            print('Failed to build {}'.format(prog))
            print('Commmand error log: {}'.format(status.stderr))
        else:
            print('Built {} succesfully'.format(prog))
        subprocess.run([get_make_command(), "clean"], capture_output=True, cwd=get_omp_c_root())
    print('Done building {}'.format(config.name))
    post_build_clean()

parser = argparse.ArgumentParser(prog='build.py', description='build NAS parallel benchmark')
parser.add_argument('config')

args = parser.parse_args()
with open(args.config) as config_file:
    config_str = config_file.read()
    for cname, config in parse_config(config_str).items():
        build_project(config)
