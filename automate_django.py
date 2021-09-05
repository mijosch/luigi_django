import luigi
from luigi import Task, DictParameter
import os

class insatll_env(Task):
    params = DictParameter()

    def run(self):
        assert os.system("python -m venv "+self.params["env_name"]) < 2, "Venv failed"
        activatestring = self.params["env_name"]+"\\Scripts\\activate"
        print(activatestring)
        assert os.system(activatestring) == 0, "Venv activate failed"
        with self.output().open('w') as f:
            f.write('Done')

    def output(self):
        return luigi.LocalTarget('environment.txt')
    
    def requires(self):
        return None

class install_django(Task):
    params = DictParameter()

    def run(self):
        commandstring = self.params["env_name"]+"\\Scripts\\pip install Django luigi"
        print(commandstring)
        assert os.system(commandstring) == 0, "luigi install failed"
        with self.output().open('w') as f:
            f.write('Done')

    def output(self):
        return luigi.LocalTarget('django.txt')
    
    def requires(self):
        return insatll_env(self.params)

class setup_page(Task):
    params = DictParameter()

    def run(self):
        commandstring = self.params["env_name"]+"\\Scripts\\django-admin startproject "+self.params["sitename"]
        print(commandstring)
        assert os.system(commandstring) == 0, "Django setup failed"
        with self.output().open('w') as f:
            f.write('Done')

    def output(self):
        return luigi.LocalTarget('page.txt')
    
    def requires(self):
        return install_django(self.params)


import pathlib
class migrate_db(Task):
    params = DictParameter()

    def run(self):
        #os.chdir(self.params["sitename"])
        commandstring = self.params["env_name"]+"\\Scripts\\python.exe "+str(pathlib.Path(__file__).parent.resolve())+"\\"+self.params["sitename"]+"\\manage.py migrate"
        print(commandstring)
        assert os.system(commandstring) == 0, "migrate failed"
        with self.output().open('w') as f:
            f.write('Done')

    def output(self):
        return luigi.LocalTarget('migrate.txt')
    
    def requires(self):
        return setup_page(self.params)

class run_dev(Task):
    params = DictParameter()

    def run(self):
        runscript = self.params["env_name"]+"\\Scripts\\python.exe "+str(pathlib.Path(__file__).parent.resolve())+"\\"+self.params["sitename"]+"\\manage.py runserver"
        #assert os.system() == 0, "run server failed"
        with self.output().open('w') as f:
            f.write(runscript)

    def output(self):
        return luigi.LocalTarget('run_dev.bat')
    
    def requires(self):
        return migrate_db(self.params)    

import sys
if __name__ == "__main__":
    print (sys.argv)
    pth = ''
    for item in sys.argv:
        if "cfg" in item:
            pth = item
            sys.argv.remove(item)
    print (sys.argv)
    cfgpath = pth.split("=")[-1]
    print(cfgpath)
    config = luigi.configuration.get_config()
    config.read(cfgpath)
    luigi.run()