from trader.core.util.common import generate_character_sequence, generate_random_string


def generate_client_order_id() -> str:
    max_char = 36

    zero_to_nine = "".join(generate_character_sequence(48, 58))
    a_to_z = "".join(generate_character_sequence(65, 91))
    A_to_Z = "".join(generate_character_sequence(97, 123))

    return generate_random_string(r".:/_-" + zero_to_nine + a_to_z + A_to_Z, max_char)