from unittest.mock import MagicMock
import pytest
from faker import Faker


@pytest.fixture()
def faker() -> Faker:
    return Faker(["pt_BR"])
