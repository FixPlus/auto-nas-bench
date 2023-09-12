#!/usr/bin/env python3
import os
import subprocess

def get_make_command():
    return 'make'

def get_prog_list():
    return ['BT', 'CG', 'FT', 'EP', 'IS']

def prepare_build_dir(compiler, suit_name):
    if not os.path.isdir('build'):
        os.mkdir('build')
    build_dir = os.path.join('build', '{}_{}'.format(compiler, suit_name))
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
def configure_project(compiler, suit_name):
    with open("make.def.in", "r") as make_template:
        template_str = make_template.read()
        config_str = template_str.format(compiler=compiler, linked_libs='-lm', 
                additional_macros='', c_flags='-O3 -fopenmp', 
                link_flags='-fopenmp', suit_name='{}_{}'.format(compiler, suit_name))
        config_dir = get_omp_config_dir()
        config_path = os.path.join(config_dir, 'make.def')
        with open(config_path, "w") as config_file:
            config_file.write(config_str)

def post_build_clean():
    config_path = os.path.join(get_omp_config_dir(), 'make.def')
    os.remove(config_path)

def build_project(compiler, suit_name):
    build_dir = prepare_build_dir(compiler, suit_name)
    print('Building omp-c with {} for {}'.format(compiler, suit_name))
    configure_project(compiler, suit_name)
    for prog in get_prog_list():
        status = subprocess.run([get_make_command(), prog, "CLASS=B"], capture_output=True, cwd=get_omp_c_root())
        if status.returncode != 0:
            print('Failed to build {}'.format(prog))
            print('Commmand error log: {}'.format(status.stderr))
        print('Built {} succesfully'.format(prog))
        subprocess.run([get_make_command(), "clean"], capture_output=True, cwd=get_omp_c_root())
    post_build_clean()

    

build_project("gcc", "kek")
