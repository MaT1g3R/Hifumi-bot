from pathlib import Path

_db_path = str(Path(__file__).parent.joinpath('test_data').joinpath('mock_db'))


def _clear_db(conn, cur):
    """
    Helper function to delete all rows from all tables from the db
    :param conn: the sqlite3 connection.
    :param cur: the sqlite3 cursor.
    """
    cur.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',))
    all_tables = [t[0] for t in cur.fetchall() if t[0]]
    for name in all_tables:
        cur.execute(f'DELETE FROM {name}')
    conn.commit()
    conn.close()


__all__ = ['_db_path', '_clear_db']
