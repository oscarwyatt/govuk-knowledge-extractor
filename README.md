govuk-knowledge-extractor
==============================

Use NLP to extract facts from GOV.UK content. 
The aim is to build up an extensive number of facts about the world
from GOV.UK content - as it's trusted and reliable.
It'll then be possible to put it into the Knowledge Graph
For example:

* "HMRC is a government department" -> `(HMRC)-[:INSTANCE_OF]->(department)`
* "Council tax is a tax" -> `(Council tax)-[:INSTANCE_OF]->(tax)`
* "Council tax is a tax" -> `(Council tax)-[:INSTANCE_OF]->(tax)`
* "Boris Johnson became Prime Minister on 24 July 2019" -> `(Boris Johnson)-[:IS { from: "24 July 2019" }]->(Prime Minister)`

There are many other potential relationships that are far more
interesting and powerful. One thing at a time though

> Knowledge is power

# Setup

## Python version
You will need the python interpreter version [Python 3.7.0](https://www.python.org/downloads/release/python-370/) or greater. You may need [`pyenv`](https://github.com/pyenv/pyenv) to specify the python version; which you can get using `pip install pyenv`.

## Virtual environment
Create a new python 3.7.0 [virtual environment](https://docs.python.org/3/library/venv.html). For up to date python 3 installations, you can do this by running the following from the command line:

```
python -m venv ~/.venv/govuk-knowledge-graph
```

This will create a new virtual environment in the `~/.venv/govuk-knowledge-graph`. It will create the directory if it does not yet exist.

Activate your virtual environment from the command line:

```
. ~/.venv/govuk-knowledge-graph/bin/activate
```

An alternative if new to python, is to use the [PyCharm](https://www.jetbrains.com/pycharm/) community edition. Open this repo as a project and then [specify what python interpreter to use](https://stackoverflow.com/a/51545578).

## Download mirrors

You'll need to download the govuk-production-mirror-replica mirrors. This can only be done if you're a member of GOV.UK.
It's also 25gb unzipped!

## Using pip to install necessary packages
Then install required python packages:

`pip install -r requirements.txt`

## Get `govuk-knowledge-graph`

You'll need a copy of the `govuk-knowledge-graph` repo as a sibling folder to this repo.
You'll also need to install it's requirements.
It's used as a (current) source of the GovNER NER model
