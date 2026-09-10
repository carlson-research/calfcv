Testing Guide
=============

This document explains how to run tests for ``bib-ami`` using ``pytest`` and offline network mocking.

Running Tests
-------------

Execute the test suite from the root of the repository:

.. code-block:: bash

   pytest tests/

Offline Mocking with pytest-httpx
---------------------------------

Because ``bib-ami`` is a thin client, it must not make live HTTP requests to the cloud engine during automated testing. Use ``pytest-httpx`` to deterministically mock API responses.

**Example: Mocking a Lookup**

.. code-block:: python

   from bib_ami.client import BibAmiClient

   def test_lookup_citation(httpx_mock):
       # Intercept the request and provide a static JSON response
       httpx_mock.add_response(
           url="http://127.0.0.1:8000/v1/citations/lookup?query=10.1234/test",
           json={"status": "Verified", "title": "Mocked Title"}
       )

       client = BibAmiClient()
       result = client.lookup_citation("10.1234/test")

       assert result["title"] == "Mocked Title"
