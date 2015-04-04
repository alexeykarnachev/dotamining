import configparser
from DotabuffImportInterface import Interface

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('C:/workspace/projects/dotamining/ext/config.ini')
    interface = Interface(config)
    interface.run_import()