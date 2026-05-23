from app import create_app

app = create_app()


def main() -> None:
    app.run(host="127.0.0.1", port=51816, debug=True)


if __name__ == "__main__":
    main()
