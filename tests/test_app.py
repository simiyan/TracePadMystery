import os
import app as flask_app
import pytest


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / 'test.db'
    flask_app.DATABASE = str(db_path)
    flask_app.init_db()
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as client:
        yield client


def test_login_flow(client):
    # initial page
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Login' in rv.data

    # perform login
    rv = client.post('/api/login', json={'username': 'alice'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'token' in data
    assert 'token=' in rv.headers.get('Set-Cookie', '')

    # mypage accessible
    rv = client.get('/mypage')
    assert rv.status_code == 200
    assert b'alice' in rv.data

    # visiting root redirects to mypage when logged in
    rv = client.get('/', follow_redirects=False)
    assert rv.status_code == 302
    assert rv.headers['Location'].endswith('/mypage')

    # logout
    rv = client.post('/logout')
    assert rv.status_code == 200

    # after logout cannot access mypage
    rv = client.get('/mypage', follow_redirects=False)
    assert rv.status_code == 302
    assert rv.headers['Location'].endswith('/')
