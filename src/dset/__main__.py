from dset.config import build_config

def main():
    success, config = build_config()
    if not success:
        return

    try:
        config.args.func(config)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
