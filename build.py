from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin('python.pycharm')


name = "dotamining"
default_task = "publish"


@init
def set_properties(project):
    pass
