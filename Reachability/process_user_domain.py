import idna


def process_user_domain(user_input: str) -> str:
    """Encode a user-supplied domain using IDNA encoding."""
    encoded = idna.encode(user_input)
    return encoded.decode("ascii")


if __name__ == "__main__":
    domain = input("Enter domain: ")
    print(process_user_domain(domain))
