===========
Using Morp
===========


Quick Start
=============

Installing Morp::

   pipenv install morpfw

Creating a simple CRUD application

.. literalinclude:: exampleapp.py
   :language: python

save as ``myapp.py``, and you can run it using::

   python myapp.py

Accessing API
==============

Morp API endpoints requires authentication (we haven't figure out how to make
it optional yet), and the default authentication policy is to acquire current
username from ``user.id`` GET parameter.

.. code-block:: python

   >>> resp = requests.get('http://localhost:5000/pages?user.id=foo'))
   >>> resp.json()

Lets create a page

.. code-block:: python

   >>> resp = requests.post('http://localhost:5000/pages/?user.id=foo', json={
   ...     'body': 'hello world'
   ... })
   >>> objid = resp.json()['data']['uuid']
   >>> resp = requests.get('http://localhost:5000/pages/%s?user.id=foo' % objid)
   >>> resp.json()
