from chak.db import repository as repos
from chak.db.schema import UserAccount
from faker import Faker

faker = Faker()

def test_user_accounts():
    account = UserAccount(
        email=faker.email()
    )
    repos.create_user_account(account)

    assert account.id is not None
    assert account.created_at is not None
    assert account.updated_at is not None    

    account_get = repos.get_user_account(account.id)
    assert account_get.id == account.id
    assert account_get.email == account.email
    # assert account_get.created_at == account.created_at
    # assert account_get.updated_at == account.updated_at
    
    