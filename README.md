#About

FairyBBS( [DEMO](http://fairybbs.com) ) is a BBS built on top of Django.

The reason it exists is that I like [June](https://github.com/pythoncn/june) from python-china.org but I'm not familiar with Flask.

You may need to know that this BBS is a Django project rather than an App. 
So, some modifications are needed to integrate the forum app into your own project

Besides, [June](https://github.com/pythoncn/june) is better in many ways compared with this project.

#Deployment

__Django has a great document that tells how to deploy a project in production [HERE](https://docs.djangoproject.com/en/1.6/howto/deployment/)__

If you just want to have a preview or a develop environment you can follow the steps below

It's recommended that you deploy this project with  virtualenv.

_It took for granted that you have pip installed and cloned or downloaded the source files from github_

1. install virtualenv: `pip install virtualenv`

2. setup a virtualenv: `virtualenv fairybbs`

3. activate the virtualenv: `source ./fairybbs/bin/activate`

5. `cd` into the folder that contains FairyBBS project

4. install the requirements: `pip install -r requirements.txt`

6. now you have to configure the database and some other settings in `conf.py` and `settings.py` in the folder `fairy` to fit you needs (__Don't forget the secret_key!__)

7. you can then run `python manage.py syncdb` to set up your database and add a superuser (If you want to use south you can turn to [its documents](http://south.readthedocs.org/en/latest/))

8. run `python manage.py runserver 0.0.0.0:8000`, then you can access to your bbs via `http://ip:8000`

9. head to `http://ip:8000/admin/`, sign in as superuser and add a profile for this superuser
