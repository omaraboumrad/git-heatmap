import sys
import datetime
import collections

import click
import git

Year = collections.namedtuple('Range', ['start', 'end'])(
    start=datetime.date.today().replace(month=1, day=1),
    end=datetime.date.today().replace(month=12, day=31)
)

def generate_unique_commits(path, author, branches, start, end):
    """
    Load unique commits from a git repository.
    Uniqueness is identified by the commit hash,
    obviously across all branches.
    """
    try:
        repo = git.repo.Repo(path)
    except git.exc.InvalidGitRepositoryError:
        print(f'Invalid git repository: {path}', file=sys.stderr)
        sys.exit(1)

    target_branches = branches or repo.branches
    found = []

    for branch in target_branches:
        # Could this be done in one go?
        for commit in repo.iter_commits(branch):
            if commit.hexsha in found:
                continue
            elif (
                # This is slow for large repos, date filtering
                # and author filtering shoudl happen via git
                # and not as a post-condition
                start <= commit.authored_datetime.date() <= end
                and (not author or commit.author.email == author)
            ):
                yield commit.authored_datetime.date()
            else:
                # nothing to do
                pass

            found.append(commit.hexsha)


def group_by_date(days):
    """
    Grouping is done by date since heatmap aggregates
    based on the date. This is a simple group by date
    done manually and not via groupby because the
    latter expects a sorted list.
    """
    grouped = collections.defaultdict(int)

    for day in days:
        grouped[day] += 1
    return grouped


def generate_heatmap(repo, author, branches, start, end, density_map):
    """
    Generates a heatmap
        between: start and end
        for: repository
        density: map total commits to known density
    """
    unique_commits = generate_unique_commits(
        path=repo,
        author=author,
        branches=branches,
        start=start,
        end=end
    )

    grouped_commits = group_by_date(unique_commits)

    heatmap = [[], [], [], [], [], [], []]
    month_start_columns = []
    current_day = start
    day_of_week = (start.weekday() + 1) % 7

    # prefill earlier days with 0
    # Alternatively in earlier stages, figure
    # out the day of week for the start date
    # and add the _actual_ previous days
    if day_of_week != 0:
        for i in range(day_of_week):
            heatmap[i].append(0)

    while current_day <= end:  # O(n)

        # This particular block will be used to calculate
        # where a specific month label (Jan, Feb...) should
        # start.
        month_abbrev = current_day.strftime('%b')
        if current_day == start:
            month_start_columns.append((0, month_abbrev))
        elif current_day.day == 1:
            month_start_columns.append((len(heatmap[day_of_week]), month_abbrev))

        value = grouped_commits.get(current_day, 0)
        density = next(v for func, v in density_map if func(value))
        heatmap[day_of_week].append(density)
        current_day += datetime.timedelta(days=1)
        day_of_week = (current_day.weekday() + 1) % 7

    return heatmap #, month_start_columns


def visualize(heatmap, color_map, character):
    """Heatmap visualization"""
    # def show_months(month_start_columns, max_columns, character):
    #     left_padding = 3  # Size of the day column
    #     print(" " * left_padding, end="")
    #     skip = 0
    #     for i in range(max_columns):
    #         months = [month for idx, month in month_start_columns if idx == i]
    #         if months:
    #             print(months[0], end='')
    #             skip = 2
    #         elif skip > 0:
    #             skip -= 1
    #         else:
    #             print(' ' * len(character), end='')
    #
    #     print('')
    #
    # heatmap, month_start_columns = heatmap
    # show_months(month_start_columns, len(heatmap[0]), character)

    days = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
    for day, row in zip(days, heatmap):
        print(day, end=" ")
        for value in row:
            print(f"{color_map[value]}{character}\033[0m", end="")
        print()


def vali_date(ctx, param, value):
    if isinstance(value, tuple):
        return value

    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise click.BadParameter("format must be 'NdM'")


def amplify(rgb, rate):
    rgb = [int(x) for x in rgb.split(';')]
    return ';'.join(str(int(x * rate)) for x in rgb)


@click.command()
@click.option('--repo', '-r', default='.', help='Path to git repository (can be relative)')
@click.option('--author', '-a', default=None, help='Author email (default all authors)')
@click.option('--branch', '-b', default=[], multiple=True, help='Branch (default all branches)')
@click.option('--start', '-s', default=Year.start, callback=vali_date, help='Start date (YYYY-MM-DD, defaults to current year start)')
@click.option('--end', '-e', default=Year.end, callback=vali_date, help='End date (YYYY-MM-DD, defaults to current year end)')
@click.option('--character', '-c', default='▧', help='Character to use for heatmap (defaults to ▧)')
@click.option('--shade', '-sh', default='0;255;0', help='Color to use for heatmap (defaults to 0;255;0)')
def run(repo, author, branch, start, end, character, shade):

    visualize(
        heatmap=generate_heatmap(
            repo=repo,
            author=author,
            branches=branch,
            start=start,
            end=end,
            density_map=[
                (lambda x: not x, 0),
                (lambda x: 1 <= x < 3, 1),
                (lambda x: 3 <= x < 6, 2),
                (lambda x: 6 <= x < 8, 3),
                (lambda x: 8 <= x, 4),
            ]
        ),
        color_map=[
            f"\033[1m",  # default
            f"\033[38;2;{amplify(shade, 1)}m",    # bright
            f"\033[38;2;{amplify(shade, 0.7)}m",  # darker
            f"\033[38;2;{amplify(shade, 0.4)}m",  # very dark
            f"\033[38;2;{amplify(shade, 0.2)}m",  # darkest
        ],
        character=f'{character} '
    )


if __name__ == '__main__':
    run()
