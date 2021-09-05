import luigi
from luigi import Task, DictParameter
import os
import pathlib

root_path = str(pathlib.Path(__file__).parent.resolve())

class insatll_env(Task):
    params = DictParameter()

    def run(self):
        self.requires()
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
        self.requires()
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
        self.requires()
        commandstring = self.params["env_name"]+"\\Scripts\\django-admin startproject "+self.params["sitename"]
        print(commandstring)
        assert os.system(commandstring) == 0, "Django setup failed"
        with self.output().open('w') as f:
            f.write('Done')

    def output(self):
        return luigi.LocalTarget('page.txt')
    
    def requires(self):
        return install_django(self.params)



class migrate_db(Task):
    params = DictParameter()

    def run(self):
        self.requires()
        #os.chdir(self.params["sitename"])
        commandstring = self.params["env_name"]+"\\Scripts\\python.exe "+root_path+"\\"+self.params["sitename"]+"\\manage.py migrate"
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
        self.requires()
        runscript = self.params["env_name"]+"\\Scripts\\python.exe "+root_path+"\\"+self.params["sitename"]+"\\manage.py runserver"
        #assert os.system() == 0, "run server failed"
        with self.output().open('w') as f:
            f.write(runscript)

    def output(self):
        return luigi.LocalTarget('run_dev.bat')
    
    def requires(self):
        return migrate_db(self.params)    

class create_apps(Task):
    params = DictParameter()
    
    def requires(self):
        return run_dev(self.params)  

    def run(self):
        print(self.input().exists())
        os.chdir(os.path.join(root_path,self.params["sitename"]))
        python_path = os.path.join(root_path,self.params["env_name"]+"\\Scripts\\python.exe")
        managepy_path = os.path.join(root_path,self.params["sitename"]+"\\manage.py")
        print(python_path)
        for item in self.params["apps"]:
            commandstring = python_path+" "+managepy_path+" startapp "+ item
            print(commandstring)
            assert os.system(commandstring) == 0, "migrate failed"
        
        os.chdir(root_path)
        with self.output().open('w') as f:
            f.write("Done")

    def output(self):
        os.chdir(root_path)
        return luigi.LocalTarget('create_apps.txt')
    
  
class clean_up(Task):
    params = DictParameter()
    
    def requires(self):
        return create_apps(self.params)  

    def run(self):
        os.remove("environment.txt")
        os.remove("django.txt")
        os.remove("page.txt")
        os.remove("migrate.txt")
        os.remove("create_apps.txt")
        with self.output().open('w') as f:
            f.write("Done")

    def output(self):
        os.chdir(root_path)
        return luigi.LocalTarget('cleanup.txt')
    

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
    #luigi.build([create_apps()],local_scheduler=True)