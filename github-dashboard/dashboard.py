import sys
import requests
from datetime import datetime
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box


def fetch_profile(username):
    url = f"https://api.github.com/users/{username}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def fetch_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=updated"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def fetch_all_languages(username, repos):
    """Fetch actual byte counts per language across all repos."""
    totals = Counter()
    for repo in repos:
        if repo.get("fork"):
            continue
        url = f"https://api.github.com/repos/{username}/{repo['name']}/languages"
        r = requests.get(url)
        if r.status_code == 200:
            for lang, bytes_count in r.json().items():
                totals[lang] += bytes_count
    return totals


def get_total_stars(repos):
    return sum(r.get("stargazers_count", 0) for r in repos)


def years_active(created_at):
    created = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.now().year - created.year


def display_dashboard(username):
    console = Console()

    with console.status(f"[bold green]Fetching GitHub data for @{username}..."):
        profile = fetch_profile(username)
        repos = fetch_repos(username)
        lang_bytes = fetch_all_languages(username, repos)

    # ── Profile ──────────────────────────────────────────────────────────────
    name = profile.get("name") or username
    bio = profile.get("bio") or ""
    location = profile.get("location") or "N/A"
    company = profile.get("company") or "N/A"
    created_at = profile.get("created_at", "")
    joined = (
        datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%B %Y")
        if created_at
        else "N/A"
    )

    profile_text = Text()
    profile_text.append(f"  {name}\n", style="bold white")
    profile_text.append(f"  @{username}\n", style="dim")
    if bio:
        profile_text.append(f"\n  {bio}\n", style="italic")
    profile_text.append(f"\n  Location :  {location}\n", style="cyan")
    profile_text.append(f"  Company  :  {company}\n", style="cyan")
    profile_text.append(f"  Joined   :  {joined}\n", style="cyan")

    console.print()
    console.print(
        Panel(profile_text, title="[bold cyan]GitHub Profile[/]", border_style="cyan")
    )

    # ── Stats ────────────────────────────────────────────────────────────────
    total_stars = get_total_stars(repos)
    public_repos = profile.get("public_repos", 0)
    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    active_years = years_active(created_at) if created_at else 0

    stats = Table.grid(expand=True)
    for _ in range(5):
        stats.add_column(justify="center")

    stats.add_row(
        f"[bold yellow]{public_repos}[/]\n[dim]Repos[/]",
        f"[bold yellow]{total_stars}[/]\n[dim]Stars[/]",
        f"[bold yellow]{followers}[/]\n[dim]Followers[/]",
        f"[bold yellow]{following}[/]\n[dim]Following[/]",
        f"[bold yellow]{active_years}[/]\n[dim]Years Active[/]",
    )

    console.print(
        Panel(stats, title="[bold yellow]Stats[/]", border_style="yellow")
    )

    # ── Top Languages ─────────────────────────────────────────────────────────
    total_bytes = sum(lang_bytes.values())
    top_langs = lang_bytes.most_common(8)

    lang_table = Table(
        show_header=True, header_style="bold magenta", box=box.SIMPLE, expand=True
    )
    lang_table.add_column("Language", style="white")
    lang_table.add_column("KB", justify="right", style="yellow")
    lang_table.add_column("", style="magenta")  # bar
    lang_table.add_column("Share", justify="right", style="cyan")

    for lang, byte_count in top_langs:
        pct = (byte_count / total_bytes * 100) if total_bytes else 0
        bar = "█" * int(pct / 3)
        lang_table.add_row(lang, f"{byte_count // 1024}", bar, f"{pct:.1f}%")

    console.print(
        Panel(
            lang_table,
            title="[bold magenta]Top Languages[/]",
            border_style="magenta",
        )
    )

    # ── Notable Repos ─────────────────────────────────────────────────────────
    top_repos = sorted(
        repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
    )[:6]

    repo_table = Table(
        show_header=True, header_style="bold blue", box=box.SIMPLE, expand=True
    )
    repo_table.add_column("Repository", style="white")
    repo_table.add_column("Language", style="cyan")
    repo_table.add_column("Stars", justify="right", style="yellow")
    repo_table.add_column("Forks", justify="right", style="green")
    repo_table.add_column("Description", style="dim")

    for repo in top_repos:
        desc = (repo.get("description") or "")[:55]
        lang = repo.get("language") or "-"
        repo_table.add_row(
            repo["name"],
            lang,
            str(repo.get("stargazers_count", 0)),
            str(repo.get("forks_count", 0)),
            desc,
        )

    console.print(
        Panel(
            repo_table,
            title="[bold blue]Notable Repos[/]",
            border_style="blue",
        )
    )

    # ── Recent Activity ───────────────────────────────────────────────────────
    recent = sorted(
        repos, key=lambda r: r.get("updated_at", ""), reverse=True
    )[:6]

    recent_table = Table(
        show_header=True, header_style="bold green", box=box.SIMPLE, expand=True
    )
    recent_table.add_column("Repository", style="white")
    recent_table.add_column("Language", style="cyan")
    recent_table.add_column("Last Updated", justify="right", style="yellow")

    for repo in recent:
        updated = datetime.strptime(
            repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%d %b %Y")
        lang = repo.get("language") or "-"
        recent_table.add_row(repo["name"], lang, updated)

    console.print(
        Panel(
            recent_table,
            title="[bold green]Recent Activity[/]",
            border_style="green",
        )
    )
    console.print()


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "kpmasud"
    display_dashboard(username)
