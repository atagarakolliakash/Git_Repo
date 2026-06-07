"""
Command-line interface for VM Automation Agent
"""

import click
import json
from pathlib import Path
from .agent import VMAutomationAgent
from .logger import setup_logger

logger = setup_logger(__name__)


@click.group()
def main():
    """VM Automation Agent - Auto-start PostgreSQL VMs and seed database"""
    pass


@main.command()
@click.option('--config', '-c', type=click.Path(), 
              help='Path to configuration file')
@click.option('--db-host', default='localhost',
              help='Database host')
@click.option('--db-port', default=5432, type=int,
              help='Database port')
@click.option('--db-user', default='postgres',
              help='Database user')
@click.option('--db-password', default='postgres',
              help='Database password')
@click.option('--db-name', default='postgres',
              help='Database name')
def run(config, db_host, db_port, db_user, db_password, db_name):
    """Run the automation workflow once"""
    click.echo("🚀 Starting VM Automation Agent...")
    
    agent = VMAutomationAgent(config)
    
    # Update config if provided
    if any([db_host != 'localhost', db_port != 5432, 
            db_user != 'postgres', db_password != 'postgres']):
        agent.configure(
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_database=db_name,
        )
    
    if agent.run_once():
        click.secho("✅ Automation completed successfully!", fg='green')
    else:
        click.secho("❌ Automation failed!", fg='red')


@main.command()
@click.option('--config', '-c', type=click.Path(),
              help='Path to configuration file')
@click.option('--db-host', default=None,
              help='Database host')
@click.option('--db-port', default=None, type=int,
              help='Database port')
@click.option('--db-user', default=None,
              help='Database user')
@click.option('--db-password', default=None,
              help='Database password')
@click.option('--db-name', default=None,
              help='Database name')
@click.option('--vbox-path', default=None,
              help='Path to VBoxManage executable')
@click.option('--enable-notifications/--disable-notifications',
              default=True,
              help='Enable/disable desktop notifications')
def configure(config, db_host, db_port, db_user, db_password, db_name, 
              vbox_path, enable_notifications):
    """Configure the agent"""
    click.echo("⚙️  Configuring VM Automation Agent...")
    
    agent = VMAutomationAgent(config)
    
    kwargs = {}
    if db_host:
        kwargs['db_host'] = db_host
    if db_port:
        kwargs['db_port'] = db_port
    if db_user:
        kwargs['db_user'] = db_user
    if db_password:
        kwargs['db_password'] = db_password
    if db_name:
        kwargs['db_database'] = db_name
    if vbox_path:
        kwargs['vbox_vbox_path'] = vbox_path
    
    kwargs['notify_enable_popup'] = enable_notifications
    
    if agent.configure(**kwargs):
        click.secho("✅ Configuration saved!", fg='green')
        
        # Show current config
        config_file = agent.config.config_file
        if Path(config_file).exists():
            with open(config_file) as f:
                current_config = json.load(f)
            click.echo("\nCurrent configuration:")
            click.echo(json.dumps(current_config, indent=2))
    else:
        click.secho("❌ Configuration failed!", fg='red')


@main.command()
@click.option('--config', '-c', type=click.Path(),
              help='Path to configuration file')
def status(config):
    """Show agent status"""
    agent = VMAutomationAgent(config)
    
    status_info = agent.get_status()
    
    click.echo("🔍 VM Automation Agent Status:")
    click.echo(f"  Running: {status_info['running']}")
    click.echo(f"  VBoxManage: {status_info['vbox_path']}")
    click.echo(f"  PostgreSQL VMs: {', '.join(status_info['pg_vms']) or 'None found'}")
    click.echo(f"  Config file: {status_info['config_file']}")
    
    if status_info['last_execution']:
        from datetime import datetime
        last_run = datetime.fromtimestamp(status_info['last_execution'])
        click.echo(f"  Last execution: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")


@main.command()
@click.option('--config', '-c', type=click.Path(),
              help='Path to configuration file')
@click.option('--daemonize/--no-daemonize', default=False,
              help='Run as background daemon (Unix only)')
def daemon(config, daemonize):
    """Start the agent as a daemon (listens for system events)"""
    click.echo("🚀 Starting VM Automation Agent daemon...")
    click.echo("Press Ctrl+C to stop.")
    
    agent = VMAutomationAgent(config)
    
    try:
        agent.start()
        
        # Keep running
        import signal
        signal.signal(signal.SIGINT, lambda sig, frame: agent.stop())
        
        while agent.is_running:
            import time
            time.sleep(1)
    
    except KeyboardInterrupt:
        click.echo("\n⏹️  Stopping agent...")
        agent.stop()
    except Exception as e:
        click.secho(f"❌ Error: {e}", fg='red')
        agent.stop()


@main.command()
@click.option('--config', '-c', type=click.Path(),
              help='Path to configuration file')
def show_config(config):
    """Display current configuration"""
    agent = VMAutomationAgent(config)
    
    config_file = agent.config.config_file
    
    if Path(config_file).exists():
        with open(config_file) as f:
            current_config = json.load(f)
        click.echo(f"Configuration file: {config_file}\n")
        click.echo(json.dumps(current_config, indent=2))
    else:
        click.echo(f"No configuration file found at {config_file}")
        click.echo("\nCreating default configuration...")
        agent.config.save_to_file()
        click.secho(f"✅ Default config created at {config_file}", fg='green')


@main.command()
@click.option('--config', '-c', type=click.Path(),
              help='Path to configuration file')
def list_vms(config):
    """List all PostgreSQL VMs"""
    click.echo("📋 Scanning for PostgreSQL VMs...")
    
    agent = VMAutomationAgent(config)
    pg_vms = agent.vbox_manager.find_pg_vms()
    
    if pg_vms:
        click.echo(f"\nFound {len(pg_vms)} PostgreSQL VM(s):")
        for vm in pg_vms:
            state = agent.vbox_manager.get_vm_state(vm)
            state_emoji = "🟢" if state == "running" else "🔴"
            click.echo(f"  {state_emoji} {vm} ({state})")
    else:
        click.secho("⚠️  No PostgreSQL VMs found", fg='yellow')


@main.command()
def init_config():
    """Initialize a new configuration file in the default location"""
    from .config import Config
    
    config = Config()
    config.save_to_file()
    
    click.secho(f"✅ Configuration initialized at {config.config_file}", fg='green')
    click.echo(f"\nYou can now edit the configuration file:")
    click.echo(f"  {config.config_file}")
    click.echo("\nThen run:")
    click.echo(f"  vm-agent run")


if __name__ == '__main__':
    main()