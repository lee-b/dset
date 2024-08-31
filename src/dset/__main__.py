from dset.config import build_config

def main():
    success, config = build_config()
    if not success:
        return

    config.args.func(config)

if __name__ == "__main__":
    main()
