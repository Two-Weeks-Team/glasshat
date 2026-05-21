from glasshat.shared.ids import canonical_json, new_uuid, sha256_hex


def test_canonical_json_is_key_sorted_and_compact() -> None:
    a = canonical_json({"b": 1, "a": [3, 2]})
    b = canonical_json({"a": [3, 2], "b": 1})
    assert a == b == '{"a":[3,2],"b":1}'


def test_canonical_json_preserves_unicode() -> None:
    assert canonical_json({"k": "디자인"}) == '{"k":"디자인"}'


def test_sha256_hex_is_stable_and_64_hex() -> None:
    h = sha256_hex("abc")
    assert h == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert len(h) == 64


def test_new_uuid_unique_v4() -> None:
    assert new_uuid() != new_uuid()
    assert len(new_uuid()) == 36
