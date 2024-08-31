from dset.config import build_config

def main():
    config = build_config()
    config.operation(config)

if __name__ == "__main__":
    main()
