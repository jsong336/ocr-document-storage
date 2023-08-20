from chak.db import repository as repos
from chak.db.schema import UserAccount, Document
from faker import Faker

faker = Faker()


def test_user_accounts():
    account = UserAccount(email=faker.email())
    repos.create_user_account(account)

    assert account.id is not None
    assert account.created_at is not None
    assert account.updated_at is not None

    account_get = repos.get_user_account_by_email(account.id)
    assert account_get.id == account.id
    assert account_get.email == account.email
    # assert account_get.created_at == account.created_at
    # assert account_get.updated_at == account.updated_at


def test_documents():
    account = UserAccount(email=faker.email())
    repos.create_user_account(account)

    document = Document(owner_id=account.id, title=faker.name())
    repos.create_document(document)

    assert document.id is not None
    assert document.created_at is not None
    assert document.updated_at is not None

    document_get = repos.get_document(document.id)
    assert document_get.id == document_get.id
    assert document_get.title == document_get.title
    assert document_get.owner_id == document_get.owner_id
