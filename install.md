# How to setup project to run on your local machine

## Requirements

- Python >= 3.12.1
  - Recommended: [Macadmins python](https://github.com/macadmins/python)
- Ruby >= 3.4.4

## Python Instructions

Follow the below instructions to setup the environment to work with the project.

### Create virtual environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Update and install tools

```bash
python3 -m pip install --upgrade pip setuptools wheel

python3 -m pip install --upgrade -r requirements.txt
```

### Install as a uv tool

```bash
uv tool install .
```

After installation, the `mscp` command can be run from any directory. Built-in
configuration, schemas, templates, images, baselines, rules, and Ruby Gemfiles
are loaded from the installed package. Generated output, writable custom
content, and Bundler-installed Ruby gems default to the user's MSCP config
directory.

Optional path overrides:

```bash
MSCP_CONFIG_FILE=/path/to/config.yaml mscp -h
MSCP_CONFIG_DIR=/path/to/mscp-config mscp -h
MSCP_CUSTOM_DIR=/path/to/custom mscp -h
MSCP_OUTPUT_DIR=/path/to/build mscp -h
```

## Ruby instructions

### Setup bundle configuration file

```bash
bundle config path mscp_gems
bundle config bin mscp_gems/bin
```

### Install ruby tools

```bash
bundle install
bundle binstubs --all
```
