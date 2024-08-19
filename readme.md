# NetWatch Pro API


This repository is a place for the NetWatch Pro backend application team to work on
the RESTful API changes and features, and to solicit and accept
[feedback and requests](https://github.com/gpapadopp/netwatch-pro-api/issues).

# NetWatch Pro API Team

As of July 2024, the NetWatch Pro backend team consists of:

* George Papadopoulos ([@gpapadopp](https://github.com/gpapadopp)), Software Engineer

## Contributing

Anyone can participate in the discussion about RESTful API changes
by adding issues in this repository,
by replying to issues in this repository,
and by uploading documents, tests or other resources.

When commenting on issues in this repository, keep in mind:

-   :+1: reactions are more useful than comments to show support.
-   Motivating examples help us understand why you want new features more than
    pointers to other examples which have them. We love hearing feedback about
    your experiences with other RESTful APIs, but we also want to know why they are
    right for this project in particular.

## License & patents

See [LICENSE][license].

## Project Build

Either you can just clone the latest built Docker imager from the [Repository's Packages][packages],
or you can create a new Docker build based on the [Dockerfile][docker_file] located in the project's root directory.
The default listening IP address and port mapping is 0.0.0.0:8000.

## Pre-requirements

In order to use this RESTful API, you have to install [MongoDB][mongo_db_site] to your local node.
The MongoDB's listening IP address and port mapping must be the 127.0.0.1:27017 (the MongoDB default).
A new Database under the name "netwatch_pro_db" is required in the MongoDB.
The application will automatically create any missing collection(s), based on the [application's config file][application_config_file].
Any changes made in the [application's config file][application_config_file] requires a new Docker build.

## Run

To run this RESTful API you just have to run the equivalent Docker build.
Automatically the Docker build will start the application and expose the port 8000 (application's default).
Then your application is ready to use. You can either access it via your local node's IP address and port mapping (http://127.0.0.1:8000),
or by implementing a [Reverse-Proxy Technique][reverse_proxy_technique_site] to your domain or public IP address.

[license]: https://github.com/gpapadopp/netwatch-pro-api/blob/main/LICENSE
[packages]: https://github.com/gpapadopp/netwatch-pro-api/pkgs/container/netwatch-pro-api
[docker_file]: https://github.com/gpapadopp/netwatch-pro-api/blob/main/Dockerfile
[mongo_db_site]: https://www.mongodb.com
[application_config_file]: https://github.com/gpapadopp/netwatch-pro-api/blob/main/config/db.py
[reverse_proxy_technique_site]: https://en.wikipedia.org/wiki/Reverse_proxy