from uri import URI
import time

class OAuth2:
    def __init__(self, client_id: str, client_secret: str, code_endpoint: URI, redirect_uri: URI, scopes: list[str]):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: URI = redirect_uri
        self.code_endpoint: URI = code_endpoint
        self.scopes: list[str] = scopes
        self.access_token: str = ''
    
    def parse_code_uri_request(self) -> str:
        uri = self.code_endpoint
        query_dict ={
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': str(self.redirect_uri),
            'scope': '%20'.join(self.scopes)
        }
        [uri.add_param(k, v) for k, v in query_dict.items()]
        return str(uri)


if __name__ == '__main__':
    import dotenv, threading
    from OAuth2ServerCode import app
    
    def start_server():
        server_thread = threading.Thread(target=lambda: app.run(port=4040, use_reloader=False))
        server_thread.daemon = True
        server_thread.start()
        return server_thread

    oauth2 = OAuth2(
        client_id=dotenv.get_key('config.env', 'OSM_CLIENT_ID'),
        client_secret=dotenv.get_key('config.env', 'OSM_CLIENT_SECRET'),
        code_endpoint=URI('https://master.apis.dev.openstreetmap.org/oauth2/authorize'),
        redirect_uri=URI('http://127.0.0.1:4040/oauth2/code'),
        scopes=[
            'read_prefs',
            'write_prefs',
            'write_diary',
            'write_api',
            'write_changeset_comments',
            'read_gpx',
            'write_gpx',
            'write_notes',
            'write_redactions',
            'write_blocks',
            'consume_messages',
            'send_messages',
            'openid'
        ]
    )
    print(oauth2.parse_code_uri_request())

    # Start the Flask server
    server_thread = start_server()
    
    # Wait for the user to provide the OAuth2 code
    print("Waiting for OAuth2 code...")
    while not dotenv.get_key('config.env', 'OSM_OAUTH2_CODE'):
        time.sleep(1)
    
    # Stop the server after receiving the code
    print("OAuth2 code received. Stopping server...")
    # Flask server will stop when the main program exits