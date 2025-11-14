#!/usr/bin/env python3
"""
Linux Session Saver - CLI interface
A tool to save and restore your Linux application sessions
"""

import argparse
import sys
from session_manager import SessionManager


def main():
    parser = argparse.ArgumentParser(
        description='Linux Session Saver - Save and restore your application sessions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s save my-work-session          # Save current apps
  %(prog)s load my-work-session          # Restore session
  %(prog)s list                          # List all sessions
  %(prog)s show my-work-session          # Show session details
  %(prog)s delete my-work-session        # Delete a session
  %(prog)s update my-work-session 0 2    # Remove apps at indices 0 and 2
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Save command
    save_parser = subparsers.add_parser('save', help='Save current session')
    save_parser.add_argument('name', help='Name for the session')

    # Load command
    load_parser = subparsers.add_parser('load', help='Load and execute a session')
    load_parser.add_argument('name', help='Name of the session to load')

    # List command
    list_parser = subparsers.add_parser('list', help='List all saved sessions')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show session details')
    show_parser.add_argument('name', help='Name of the session to show')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a session')
    delete_parser.add_argument('name', help='Name of the session to delete')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update session (remove apps)')
    update_parser.add_argument('name', help='Name of the session to update')
    update_parser.add_argument('indices', nargs='+', type=int,
                              help='Indices of apps to remove (see "show" command)')

    # Scan command (show current apps without saving)
    scan_parser = subparsers.add_parser('scan', help='Scan and display current running apps')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = SessionManager()

    try:
        if args.command == 'save':
            return 0 if manager.save_session(args.name) else 1

        elif args.command == 'load':
            return 0 if manager.load_session(args.name) else 1

        elif args.command == 'list':
            sessions = manager.list_sessions()
            if not sessions:
                print("No saved sessions")
                return 0

            print(f"\nSaved sessions ({len(sessions)}):\n")
            for name, data in sessions.items():
                app_count = len(data['apps'])
                created = data['created'].split('T')[0]  # Just date
                print(f"  • {name}")
                print(f"    Created: {created}")
                print(f"    Apps: {app_count}")
                print()
            return 0

        elif args.command == 'show':
            manager.show_session(args.name)
            return 0

        elif args.command == 'delete':
            return 0 if manager.delete_session(args.name) else 1

        elif args.command == 'update':
            return 0 if manager.update_session(args.name, args.indices) else 1

        elif args.command == 'scan':
            apps = manager.get_running_apps()
            if not apps:
                print("No applications detected")
                return 0

            print(f"\nCurrently running applications ({len(apps)}):\n")
            for idx, app in enumerate(apps):
                print(f"  [{idx}] {app['name']}")
                print(f"      Command: {app['command']}")
                print()
            return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
