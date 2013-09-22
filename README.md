# Orthosie #

Orthosie is a point of sale system written in Python using the Django framework. Currently Orthosie supports Python 2 & 3 and Django 1.5.

## Installation 

Orthosie uses Django REST Framework. It can be grabbed from http://django-rest-framework.org/

Getting Orthosie running for the first time requires that we setup the sqlite database file:
    
    # cd orthosie
    # ./manage.py syncdb

To run the test server: 

    # cd orthosie
    # ./manage.py runserver

At this point you can browse to http://127.0.0.1:8000/register/ to see the register.

There is currently no easy way to add any inventory to the system. Inventory can be added from the python/django shell by adding a vendor and an item. The following adds Reed's Gingerbrew:

    # ./manage.py shell
    >>> import inventory.models as inventory
    >>> v = inventory.Vendor(name='Reed''s')
    >>> v.save()
    >>> i = inventory.Item(upc='00827400006', name='Original Ginger Brew', price=1.72, scalable=False, taxable=True, vendor=v)
    >>> i.save()

At this point you should be able to ring up this product. Note that during the ring the UPC checksum is needed for a ring to go through properly, so you will need to input '008274000061' for the ring to work.

## License ##

    Copyright 2013 Jack David Baucum

    This file is part of Orthosie.

    Orthosie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Orthosie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Orthosie.  If not, see <http://www.gnu.org/licenses/>.

Orthosie is licensed under the GPLv3. The details of this license can be viewed at http://gplv3.fsf.org/ until I get around to properly adding licensing information.
