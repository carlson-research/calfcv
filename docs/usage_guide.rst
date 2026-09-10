Usage Guide
===========

This document covers command-line execution, environment variable configuration, and Python SDK usage for ``bib-ami``.

Command-Line Interface
----------------------

The CLI provides two primary commands:

.. code-block:: bash

   bib-ami launch [--url <custom_url>]
   bib-ami lookup <identifier>

The ``launch`` command accepts an optional ``--url`` flag to point the browser to a specific environment. The ``lookup`` command takes a single identifier (like a DOI) and returns the JSON payload from the remote verification engine.

Environment Variables
---------------------

You can customize the client's routing and authentication using the following environment variables:

- ``BIB_AMI_API_URL``: Custom API endpoint (defaults to ``http://127.0.0.1:8000/v1``).
- ``BIB_AMI_WEB_URL``: Custom web application target (defaults to ``https://bib-ami.com``).
- ``BIB_AMI_API_KEY``: Bearer token for authenticated API requests. Required for high-volume or commercial usage.

Python SDK Usage
----------------

The ``BibAmiClient`` class allows seamless integration into your own Python data pipelines:

.. code-block:: python

   from bib_ami.client import BibAmiClient

   # Initializes using environment variables for routing and auth
   client = BibAmiClient()

   # Returns a dictionary containing the validated citation data
   result = client.lookup_citation("10.1038/nature12345")
   print(result.get("title"))
