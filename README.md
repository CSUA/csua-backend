CSUA-backend
============

A backend for the CSUA interblags.

## Getting started

1. Install Python 2
2. Install Django with `pip install -r requirements.txt`
3. Change `DEBUG` to `True` at the top of `csua_backend/settings.py`
4. Set up server with `python2 manage.py migrate`
5. Run server with `python2 mangage.py runserver`
6. Navigate to http://127.0.0.1:8000/

## Editing/Creating/Deleting Officers

```python
C:\Users\Caleb\workspace\CSUA-backend [master +0 ~1 -0]> python manage.py shell
Python 2.7.10 (default, May 23 2015, 09:40:32) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from db_data.models import Officer
>>> Officer.objects.get(first_name = "Ashley")
<Officer: Ashley Chien>
>>> ashley = Officer.objects.get(first_name = "Ashley")
>>> ashley.blurb
u'"Cats"'
>>> ashley.blurb = 'Cats'
>>> ashley.save()
>>> loren = Officer.objects.get(first_name = "Loren")
>>> loren.office_hours
u'F 10-11AM'
>>> loren.office_hours = 'Fri 10-11AM'
>>> loren.save()
>>> victor = Officer.objects.create()
>>> victor.first_name = "Victor"
>>> victor.last_name = "Ye"
>>> victor.office_hours = "TBD"
>>> victor.photo1_url = "victorye.jpg"
>>> victor.blurb = "Real human bean."
>>> victor.save()
>>> Officer.objects.get(first_name = "Caleb").delete()
```