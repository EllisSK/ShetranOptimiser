from argparse import ArgumentParser, Namespace
from .cli import update_config, optimise

def main():
    print("Shetran-Optimiser v0.0.0")
    #Univeral args
    parser = ArgumentParser()

    parser.add_argument(
        "--debug", action="store_true", help="Enable debugging features"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    #Config args
    parser_config = subparsers.add_parser(
        "config", help="Alter configuration variables"
    )
    parser_config.add_argument(
        "--main-executable", type=str, help="Set path to Shetran executable"
    )
    parser_config.add_argument(
        "--prepare-executable", type=str, help="Set path to Shetran-Prepare executable"
    )
    parser_config.set_defaults(func=update_config)

    #Optimise args
    parser_optimise = subparsers.add_parser(
        "optimise", help="Optimise a set of shetran parameters"
    )
    parser_optimise.add_argument(
        "project", type=str, help="Full path to the project directory"
    )
    parser_optimise.add_argument(
        "--resume", "-r", action="store_true", help= "Resume algorithm run from a checkpoint pickle file"
    )
    parser_optimise.add_argument(
        "--algorithm", "-a", type=str, help="Algorithm type to use"
    )
    parser_optimise.set_defaults(func=optimise)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
