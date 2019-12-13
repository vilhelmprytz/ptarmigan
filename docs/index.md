# What is ptarmigan?

ptarmigan is a support ticket management system built in Python 3 and Flask.

# Application Stack

Ptarmigan is built on the Flask Python framework. It runs as a WSGI service behind your choice of HTTP server.

| Function      | Component             |
|---------------|-----------------------|
| HTTP Service  | Apache 2 or nginx     |
| WSGI Service  | gunicorn or uWSGI     |
| Application   | Flask/Python          |
| Database      | MySQL                 |
| Session Cache | Redis                 |

# Getting Started

See the [installation guide](installation.md) for help getting ptarmigan running.