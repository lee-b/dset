from dset.config import build_config

def main():
    config = build_config()
    
    # Execute the function associated with the chosen subcommand
    config.args.func(config)

if __name__ == "__main__":
    main()
