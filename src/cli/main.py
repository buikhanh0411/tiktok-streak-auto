import click
import os
import sys
import asyncio

from typing import Optional, List
# Add the project root to sys.path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.engines.playwright_engine import PlaywrightEngine
from src.engines.nodriver_engine import NodriverEngine
from src.platforms.tiktok import TikTokPlatform
from src.core.messenger import Messenger

def get_engine(engine_name: str):
    if engine_name.lower() == 'playwright':
        return PlaywrightEngine()
    elif engine_name.lower() == 'nodriver':
        return NodriverEngine()
    else:
        raise click.BadParameter(f"Unknown engine: {engine_name}. Choose 'playwright' or 'nodriver'.")

@click.group()
def cli():
    """TikTok Auto Streak Messenger CLI"""
    pass

@cli.command()
@click.option('--engine', '-e', default='nodriver', help='Browser engine to use: playwright or nodriver (default)')
def login(engine: str):
    """Manually login to TikTok and capture cookies"""
    engine_instance = get_engine(engine)
    platform = TikTokPlatform(engine_instance)
    messenger = Messenger(engine_instance, platform)
    
    click.echo(f"[*] Starting {engine} for manual login...")
    asyncio.run(messenger.login_manually())

@cli.command()
@click.option('--engine', '-e', default='playwright', help='Browser engine to use: playwright or nodriver')
def check_cookies(engine: str):
    """Check if the current cookies are still valid (healthy)"""
    engine_instance = get_engine(engine)
    platform = TikTokPlatform(engine_instance)
    messenger = Messenger(engine_instance, platform)
    
    click.echo(f"[*] Checking cookie health using {engine}...")
    success = asyncio.run(messenger.check_cookies_health())
    if not success:
        sys.exit(1)

@cli.command()
@click.option('--users', '-u', help='Comma-separated list of nicknames to message')
@click.option('--file', '-f', type=click.Path(exists=True), help='Text file containing nicknames (one per line)')
@click.option('--message', '-m', multiple=True, help='Message template (can be used multiple times for randomization)')
@click.option('--msg-file', type=click.Path(exists=True), help='Text file containing message templates (one per line)')
@click.option('--engine', '-e', default='playwright', help='Browser engine to use: playwright or nodriver')
@click.option('--footer', is_flag=True, help='FORCE include the long instruction footer message (ignore 7-day rule)')
def send(users: Optional[str], file: Optional[str], message: List[str], msg_file: Optional[str], engine: str, footer: bool):
    """Send randomized messages with streak prefix and periodic weekly instructions"""
    nicknames = []
    
    if users:
        nicknames.extend([u.strip() for u in users.split(',') if u.strip()])
    
    if file:
        with open(file, 'r') as f:
            nicknames.extend([line.strip() for line in f if line.strip()])
            
    if not nicknames:
        raise click.UsageError("You must provide either --users or --file.")

    # Collect all message templates
    templates = list(message)
    if msg_file:
        with open(msg_file, 'r') as f:
            templates.extend([line.strip() for line in f if line.strip()])

    if not templates:
        raise click.UsageError("You must provide at least one message template using -m or --msg-file.")
    
    engine_instance = get_engine(engine)
    platform = TikTokPlatform(engine_instance)
    messenger = Messenger(engine_instance, platform)
    
    click.echo(f"[*] Starting message streak for {len(nicknames)} users using {engine}...")
    # Map CLI 'footer' flag to 'force_footer' in Messenger
    asyncio.run(messenger.run_streak(nicknames, templates, force_footer=footer))

if __name__ == '__main__':
    cli()
