# leanote2md
Export all you Markdown notes in Leanote (a.k.a 蚂蚁笔记) to local Markdown files.

## Prerequisite

- Python 3
- pip3
- git

## Dependencies
Use your pip tool to install the dependencies

- anytree
- requests

You can install these packages by this command

```shell
pip3 install anytree requests --user
```

## Usage
Clone this repo, and run the `exporter.py` script. You can easily do this by running the following command on your terminal

```python
git clone https://github.com/gaunthan/leanote2md.git
cd ./leanote2md
chmod +x exporter.py
./exporter.py
```

If you don't want to save your notes interactively, you need to modify `config.py` and run `exporter.py` with command argument `config.py`

```shell
./exporter.py config.py
```
