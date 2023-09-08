# git-heatmap

Shows a heatmap for your Git repositories.

![Screenshot](screenshot.png)

## Usage

```
Usage: git-heatmap [OPTIONS]

Options:
  -r, --repo TEXT       Path to git repository (can be relative)
  -a, --author TEXT     Author email (default all authors)
  -b, --branch TEXT     Branch (default all branches)
  -s, --start TEXT      Start date (YYYY-MM-DD, defaults to current year
                        start)
  -e, --end TEXT        End date (YYYY-MM-DD, defaults to current year end)
  -c, --character TEXT  Character to use for heatmap (defaults to ▧)
  -sh, --shade TEXT     Color to use for heatmap (defaults to 0;255;0)
  --help                Show this message and exit.
```

##  Examples

Run `git-heatmap` ...

```
# in a directory that's already a git repository
$ git-heatmap

# on a repository elsewhere
$ git-heatmap -r /path/to/repo

# limit by author email
$ git-heatmap -a me@myself.com

# pick a specific branch
$ git-heatmap -b main

# pick multiple branches
$ git-heatmap -b main -b develop

# start from date
$ git-heatmap -s 2023-02-01

# end on date
$ git-heatmap -s 2023-02-28

# change characters
$ git-heatmap -c '●'

# change colors
$ git-heatmap -sh "255;255;0"
```
