from sqlalchemy import text


def test_db_session_fixture_works(db_session):
    result = db_session.execute(text("SELECT 1;"))
    assert result.scalar() == 1
