# Jira to Confluence gantt chart generator

[![Lint](https://github.com/cledouarec/jira2confluence-gantt/actions/workflows/lint.yaml/badge.svg)](https://github.com/cledouarec/jira2confluence-gantt/actions/workflows/lint.yaml)
[![Unit tests](https://github.com/cledouarec/jira2confluence-gantt/actions/workflows/test.yaml/badge.svg)](https://github.com/cledouarec/jira2confluence-gantt/actions/workflows/test.yaml)

**Table of Contents**
* [Overview](#Overview)
* [Installation](#Installation)
* [Usage](#Usage)
* [Configuration](#Configuration)
    * [Server configuration](#Server-configuration)
    * [Project configuration](#Project-configuration)

## Overview

This module has the objective to create a gantt chart from Jira data and
publish and publish the resulting chart and status on Confluence.
It provides different render engines, but it is easy to add its own custom
engine :
![Confluence engine](https://github.com/cledouarec/jira2confluence-gantt/raw/main/examples/ConfluenceChart.png)
![PlantUML engine](https://github.com/cledouarec/jira2confluence-gantt/raw/main/examples/PlantUML.png)

## Installation

### From PyPI (Recommended)

You can install the exporter easily with the following command or insert into
your requirements file :
```shell
pip install jira2confluence-gantt
```

### From sources

All the project is managed with **Poetry**. To install it, please visit the
[official page](https://python-poetry.org/docs/#installation) and follow these
instructions :
```shell
poetry shell
poetry install --without dev
```

For the developers, it is useful to install extra tools like :
* [commitizen](https://commitizen-tools.github.io/commitizen/)
* [pre-commit](https://pre-commit.com)
* [pytest](http://docs.pytest.org)
* [ruff](https://docs.astral.sh/ruff/)

These tools can be installed with the following command :
```shell
poetry install
```
The Git hooks can be installed with :
```shell
poetry run pre-commit install
```
The hooks can be run manually at any time :
```shell
poetry run pre-commit run --all-file
```

## Usage

The script with required argument can be started by executing the following
command :
```shell
jira2confluence-gantt my_config.yaml
```

The full list of arguments supported can be displayed with the following
helper :
```shell
jira2confluence-gantt -h
usage: jira2confluence-gantt [-h] [-v] [config.yaml]

positional arguments:
  config.yaml    Configuration file

options:
  -h, --help     show this help message and exit
  -v, --verbose  Verbose mode
```

## Configuration

The configuration file support 2 formats :
- [YAML format](https://yaml.org) (Recommended format)
- [JSON format](https://www.json.org)

In the configuration file, there are 2 main sections required :
- Server
- Projects

### Server configuration

The **server** node will configure the URL of the Jira and Confluence server.
For the moment, only the username/token authentication is supported.
The credentials could be defined with environment variables or `.env` file.

```
ATLASSIAN_USER=<your login>
ATLASSIAN_TOKEN=<your token>
```

**_In Yaml :_**
```yaml
server:
  jira: "https://my.jira.server.com"
  confluence: "https://my.confluence.server.com"
```
**_In Json :_**
```json
{
  "server": {
    "jira": "https://my.jira.server.com",
    "confluence": "https://my.confluence.server.com"
  }
}
```

| Attribute  | Required | Description                                                                                                                                      |
|------------|:--------:|--------------------------------------------------------------------------------------------------------------------------------------------------|
| server     |    ✅     | Main configuration node for server.                                                                                                              |
| jira       |    ✅     | Jira server URL to retrieve tickets information.                                                                                                 |
| confluence |    ❌     | Confluence server URL to publish the report. If the confluence server isn't set, only the gantt chart will be generated if the engine permit it. |

### Project configuration

The `projects` node will provide the configuration for each project.

**_In Yaml :_**
```yaml
projects:
  - name: "Project name"
    jql: "project = TEST"
    report:
      space: "SPACE"
      parent_page: "My Parent Page"
      engine: "PlantUML"
      legend: True
      template: "report.jinja2"
    fields:
      start_date: "Start date (WBSGantt)"
      end_date: "Finish date (WBSGantt)"
      progress: "Progress (WBSGantt)"
      link: "is blocked by"
```
**_In Json :_**
```json
{
  "projects": [
    {
      "name": "Project name",
      "jql": "project = TEST",
      "report": {
        "space": "SPACE",
        "parent_page": "My Parent Page",
        "engine": "PlantUML",
        "legend": true,
        "template": "report.jinja2"
      },
      "fields": {
        "start_date": "Start date (WBSGantt)",
        "end_date": "Finish date (WBSGantt)",
        "progress": "Progress (WBSGantt)",
        "link": "is blocked by"
      }
    }
  ]
}
```

| Attribute | Required | Description                                                                                                                                      |
|-----------|:--------:|--------------------------------------------------------------------------------------------------------------------------------------------------|
| projects  |    ✅     | Main configuration node for all projects.                                                                                                        |
| name      |    ✅     | Name of the project.<br/>This name will be used as a title in the Gantt chart and also as a name in Snake case format for the output gantt file. |
| jql       |    ✅     | [JQL](https://www.atlassian.com/blog/jira-software/jql-the-most-flexible-way-to-search-jira-14) query to retrieve the list of tickets.           |
| report    |    ✅     | Main configuration node for report generation.                                                                                                   |
| fields    |    ✅     | Main configuration node for fields.                                                                                                              |

Some attributes could use double quotes to preserve space in their names. The
YAML syntax provides a solution by replacing with simple quote or escaping
like JSON :

**_In Yaml :_**
```yaml
jql: 'project = "MY TEST"'
```
**_In Json :_**
```json
{
  "jql": "project = \"MY TEST\""
}
```

#### Report configuration

Configuration node for all attributes related to report generation.

| Attribute   | Required | Description                                                                |
|-------------|:--------:|----------------------------------------------------------------------------|
| space       |    ✅     | Confluence destination space.                                              |
| parent_page |    ✅     | Confluence parent page of the report page.                                 |
| engine      |    ❌     | Engine used to create gantt report. **`Confluence` is the default engine** |
| legend      |    ❌     | Add a legend in the gantt chart. **By default the legend is not added.     |

There are several engines available to produce Gantt chart :
- `Confluence` chart macro : Produce a chart with a builtin macro. The graph
  will not include the dependency link.  
  
- `PlantUML` macro : Produce a PlantUML graph which will be included in the
  Confluence page with the PlantUML macro.

#### Fields

Configuration node for all Jira fields used to construct Gantt chart.  
**It is a mandatory field.**

**_In Yaml :_**

These fields are most of the time the same for all projects and like all others
fields they could be aliased to avoid redefinition.  
In the following example, we define an anchor `WbsFields` :
```yaml
Server:
  # ...

Fields: &WbsFields
  Start date: "Start date (WBSGantt)"
  End date: "Finish date (WBSGantt)"
  Progress: "Progress (WBSGantt)"

Projects:
  Project name:
    JQL: "project = TEST"
    Fields: *WbsFields
  Second project name:
    JQL: "project = TEST2"
    Fields: *WbsFields
```

**_In Json :_**
```json
{
  "Projects": {
    "Project name": {
      "Fields": {
        "Start date": "Start date (WBSGantt)",
        "End date": "Finish date (WBSGantt)",
        "Progress": "Progress (WBSGantt)",
      }
    }
  }
}
```

#### Start date

Define the Jira field to use as a start date for task in Gantt chart.  
**It is a mandatory field.**

#### End date

Define the Jira field to use as a start date for task in Gantt chart.  
**It is a mandatory field.**

#### Progress

Define the Jira field to use as a percent of work done for task in Gantt chart.  
**It is an optional field.**

#### Link

Define the Jira inward link to use in order to define how the tasks could be
blocked by others tasks task in Gantt chart.  
**It is an optional field. By default, the link used is "is blocked by"**

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, shall be as defined in the Apache-2.0 license
without any additional terms or conditions.

See [CONTRIBUTING.md](CONTRIBUTING.md).
