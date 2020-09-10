Stad in Cijfers, python API
================

Purpose
----

A python package to make data from stadincijfers easely available for data scientists. 

Intro
-----

Via the website 'Stad in cijfers' you can consult statistical data on various themes. In principle for the city of Antwerp, all data on 'Stad in cijfers' is open data and can therefore be used freely, unless stated otherwise.

Many local goverments in Flanders have a website like this:

- Gent: https://gent.buurtmonitor.be
- Antwerp: https://stadincijfers.antwerpen.be/databank
- The provinces: https://provincies.incijfers.be

Installation:
--------------

from [pypi](https://pypi.org/project/stadincijfers/): 

    pip install stadincijfers

or from sources: 
    
    git clone https://github.com/warrieka/stadincijfers.py
    cd stadincijfers.py
    pip install -r requirements.txt
    pip install .

Usage:
-----

```python
    from stadincijfers import stadincijfers
    sic = stadincijfers("antwerpen") #or gent or provincies or url
    sic.periodlevels() #=> get all periodslevels
```

For more see example jupyter notebook: [example_usage.ipynb](example_usage.ipynb)