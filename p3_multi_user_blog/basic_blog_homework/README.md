# Multi User Blog

Udacity FSWD Project 3

# About

Multi User Blog is a basic blogging engine for multiple users.

# Contents

1. basic_blog.py
  * Contains all the classes for the page handlers, as well as helper methods for these Classes

2. models.py
  * Contains the classes for the database entity models: User, Post, Comment and Like

3. app.yaml
  * contains the configuration for google app engine

4. templates
  * contains the page layout base template, as well as all inheriting templates for page views with jinja2

5. static
  * contains the main css stylesheet as well as framework.css for grid system, and normalize.css for css reset.

# How to run the application:

Visit the application at: https://multi-user-blog-157519.appspot.com/

To run locally:

Ensure Python 2.7 is installed

```
$ python -V
```

Install Google Cloud SDK

https://cloud.google.com/appengine/docs/python/download

Clone the repo in your terminal
```
$ git clone git@github.com:Courtney2511/basic_blog_homework.git
```

Navigate to the folder where the files were installed and run:
```
$ dev_appserver.py .
```
