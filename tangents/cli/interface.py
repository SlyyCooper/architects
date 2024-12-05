import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

app = typer.Typer()
console = Console()

LOGO = """
████████╗ █████╗ ███╗   ██╗ ██████╗ ███████╗███╗   ██╗████████╗███████╗
╚══██╔══╝██╔══██╗████╗  ██║██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
   ██║   ███████║██╔██╗ ██║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗
   ██║   ██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
   ██║   ██║  ██║██║ ╚████║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝
"""

def display_logo():
    """Display the colorful T.A.N.gents logo."""
    logo_text = Text(LOGO)
    logo_text.stylize("bold magenta")
    console.print(Panel(logo_text, border_style="cyan", title="Welcome to", subtitle="Multi-Agent Framework"))
    console.print("\n[bold blue]Initializing T.A.N.gents Framework...[/bold blue]\n")

@app.command()
def main():
    """Main entry point for the T.A.N.gents CLI."""
    display_logo()
    console.print("[green]T.A.N.gents is ready! 🚀[/green]")

if __name__ == "__main__":
    app() 