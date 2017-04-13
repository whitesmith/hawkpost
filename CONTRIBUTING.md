# Contributing to Hawkpost

Given this project is in active development, with the desire to continually provide more value and better serve its users, you are more than welcome to join in and help improve Hawkpost. The project will mostly use the Github issues to keep track of bugs, feature requests and milestones. So an account should be all you need to start contributing.

Below are a few things we follow and would appreciate if you do too.

## Issues

When reporting bugs or requesting new features, please provide as much detail and context as you can. This will make things much easier to the people trying to address your issue.

## How to add/remove dependencies

* Add/remove to the correct `.in` file the required package. For dev only dependencies `requirements_dev.in`, otherwise `requirements.in`. Note: you should pin the version number.

* Compile the new requirements (You will need to install `pip-tools`)

```
$ pip-compile requirements/base.in -o requirements/requirements.txt
```

and 

```
$ pip-compile requirements/base.in requirements/development.in -o requirements/requirements_dev.txt
```

* Commit these changes alongside your other code modifications

## Style

In order to facilitate the task of everyone who is contributing to this project, we have opted to present a few guidelines here about the "code style" . These guidelines are not rigid and common sense should be taken into account when discussing this matter.

For python code, unless it is prejudicial to the given situation or makes it harder to understand the code, you should follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) convention.

For the HTML templates, you should make use of indentation (2 spaces) to make a clear distinction between parent and children elements (siblings should be on the same indentation level).
