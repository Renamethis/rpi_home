[![unittests](https://github.com/Renamethis/rpi_home/actions/workflows/python-unit.yml/badge.svg?branch=master)](https://github.com/Renamethis/rpi_home/actions/workflows/python-unit.yml)
[![functional](https://github.com/Renamethis/rpi_home/actions/workflows/python-functional.yml/badge.svg?branch=master)](https://github.com/Renamethis/rpi_home/actions/workflows/python-functional.yml)
# Raspberry PI home

It's currently monolithic, but extendable web-service for weather monitoring(weather station), displaying weather and other infromation and controlling smart-home devices(not implemented).

## Structure
Let's distribute this service on the following parts:
### Backend
Backend is based on flask web framework. It's has several endpoints for receiving different infromation, authentication(not implemented), etc. Most of the execution time running in celery-tasks in the isolated and thread-safety queued worker. This prevents from data synchronization, database queries and other problems.
SQLAlchemy is using as the ORM models for postgresql tables.

There is also two separate device threads:

- Enviro thread

This thread controls the enviroplus hat-board on raspberry pi. It's collects the weather data and represents this information on the lcd screen which located on it.

- Matrix thread

This thread controls the unicorn led matrix hat-board on raspberry. It's runs different animations, implemented in project, such as time displaying, weather displaying, rainbow animation and others.


### Frontend

Frontend based on React framework and represents two main parts:

- Graph view

This view displays the interactive graph with different weather indicators. It's possible to move graph to the oldest/newest entries, switch indicator on fly and view information about specified graph entry(by clicking).

- Weather view

This is the simple view which basically displaying current weather taken from the backend. But also it's using when you click something on the graph to take closer look.

### Android TV app

Android TV app it's separated project, but it's also integrating with the raspberry pi home. Currently it's only displaying different weather indicators.

## Set up

## Deploy

## Tests
