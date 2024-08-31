from dset.config import build_config

def main():
    config = build_config()
    if config.operation.__name__ == 'filter_handler':
        config.operation(config)
    else:
        config.operation(config)

if __name__ == "__main__":
    main()
