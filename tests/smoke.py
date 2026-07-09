from tokenlab import TOKENLAB_OPENAI_BASE_URL, TokenLabClient


def main() -> None:
    client = TokenLabClient(api_key="test-token")
    assert client.openai_base_url == TOKENLAB_OPENAI_BASE_URL
    client.close()
    print("smoke ok")


if __name__ == "__main__":
    main()
