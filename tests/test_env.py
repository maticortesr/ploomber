import platform
from pathlib import Path

import pytest
import yaml

from ploomber.env.env import _get_name, Env, with_env


def test_load_env_with_name(tmp_directory, cleanup_env):
    Path('env.some_name.yaml').write_text(yaml.dump({'a': 1}))
    Env.start('env.some_name.yaml')


def test_load_env_default_name(tmp_directory, cleanup_env):
    Path('env.yaml').write_text(yaml.dump({'a': 1}))
    Env.start()


def test_load_env_hostname(tmp_directory, cleanup_env):
    name = 'env.{}.yaml'.format(platform.node())
    Path(name).write_text(yaml.dump({'a': 1}))
    Env.start()


def test_path_returns_Path_objects(cleanup_env):
    env = Env.start({'path': {'a': '/tmp/path/file.txt',
                              'b': '/another/path/file.csv'}})
    assert isinstance(env.path.a, Path)
    assert isinstance(env.path.b, Path)


def test_init_with_module_key(cleanup_env):
    env = Env.start({'module': 'sample_project'})
    assert env.module == 'sample_project'


def test_init_with_nonexistent_package(cleanup_env):
    with pytest.raises(ImportError):
        Env.start({'module': 'i_do_not_exist'})


def test_version_placeholder(cleanup_env):
    env = Env.start({'module': 'sample_project', 'version': '{{version}}'})
    assert env.version == '0.1dev'


def test_can_create_env_from_dict(cleanup_env):
    e = Env.start({'a': 1})
    assert e.a == 1


def test_assigns_default_name():
    assert _get_name('path/to/env.yaml') == 'root'


def test_can_extract_name():
    assert _get_name('path/to/env.my_name.yaml') == 'my_name'


def test_raises_error_if_wrong_format():
    with pytest.raises(ValueError):
        _get_name('path/to/wrong.my_name.yaml')


def test_can_instantiate_env_if_located_in_sample_dir(move_to_sample_dir,
                                                      cleanup_env):
    Env.start()


def test_can_instantiate_env_if_located_in_sample_subdir(move_to_sample_subdir,
                                                         cleanup_env):
    Env.start()


def test_raise_file_not_found_if(cleanup_env):
    msg = ('Could not find file "env.non_existing.yaml" '
           'in the current working directory nor 6 levels up')
    with pytest.raises(FileNotFoundError, match=msg):
        Env.start('env.non_existing.yaml')


def test_with_env_decorator(cleanup_env):
    @with_env({'a': 1})
    def my_fn(env, b):
        return env.a, b

    assert (1, 2) == my_fn(2)
