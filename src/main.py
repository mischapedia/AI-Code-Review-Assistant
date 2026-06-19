import click
from src.reviewer import run_review
from src.config_loader import get_config
from src.logger import setup_logger

@click.group()
def cli():
    """
    CLI für den Review Assistant.
    """
    pass

@cli.command()
@click.option('--project-id', required=True, type=int, help='Die ID des GitLab Projekts.')
@click.option('--mr-id', required=True, type=int, help='Die ID des Merge Requests.')
@click.option('--dry-run', is_flag=True, help='Review nur auf der Konsole ausgeben, nicht in GitLab posten.')
def review(project_id, mr_id, dry_run):
    """
    Startet ein Code-Review für einen bestimmten Merge Request.
    """
    config = get_config()
    setup_logger(log_level=config.log_level)
    run_review(project_id, mr_id, dry_run)

@cli.command()
def check_config():
    """
    Prüft ob die Umgebungsvariablen korrekt geladen werden.
    """
    try:
        config = get_config()
        click.secho("Konfiguration erfolgreich geladen!", fg="green")
        click.echo(f"GitLab URL: {config.gitlab_url}")
        click.echo(f"LLM Provider: {config.llm_provider}")
        click.echo(f"LLM Model: {config.llm_model}")
        click.echo(f"Log Level: {config.log_level}")
    except Exception as e:
        click.secho(f"Konfigurationsfehler: {e}", fg="red")

if __name__ == '__main__':
    cli()
