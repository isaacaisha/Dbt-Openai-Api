import pytest
from app.calculation import add, substract, multiply, divide, BankAccount, InsufficientFunds


@pytest.fixture
def zero_bank_account():
    print("testing zero_bank_account function")
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(45)


@pytest.mark.parametrize("num1, num2, expected", [
    (3, 2, 5),
    (7, 1, 8),
    (12, 3, 15)
])
def test_add(num1, num2, expected):
    print("testing add function")
    assert add(num1, num2) == expected


def test_substract():
    print("testing substract function")
    assert substract(9, 4) == 5


def test_multiply():
    print("testing multiply function")
    assert multiply(3, 4) == 12


def test_divide():
    print("testing divide function")
    assert divide(20, 4) == 5


def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 45


def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_withdraw(bank_account):
    bank_account.withdraw(26)
    assert bank_account.balance == 19


def test_deposite(bank_account):
    bank_account.deposite(46)
    assert bank_account.balance == 91


def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 6) == 49.5


@pytest.mark.parametrize("deposited, withdraw, expected", [
    (199, 90, 109),
    (73, 18, 55),
    (1200, 200, 1000)
])
def test_bank_transaction(zero_bank_account, deposited, withdraw, expected):
    zero_bank_account.deposite(deposited)
    zero_bank_account.withdraw(withdraw)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(199)
