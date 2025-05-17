import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional
import requests, dotenv
from bs4 import BeautifulSoup

ENVIRONMENT_PATH = 'config.env'

class OsmXml(ET.Element):
    def __init__(self):
        super().__init__('osm')

    def __str__(self):
        return ET.tostring(self, encoding='unicode')

@dataclass
class Changeset:
    author: str
    comment: str

@dataclass
class Node:
    lat: float
    lon: float
    tags: dict[str, str]
    changeset_id: Optional[str] = None

class OSM:
    """
    Classe para interagir com a API do OpenStreetMap.
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list[str]):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: str = redirect_uri
        self.scopes: str = '%20'.join(scopes)

        self.main_url = "https://master.apis.dev.openstreetmap.org"

        try:
            self.access_token = dotenv.get_key(ENVIRONMENT_PATH, 'OSM_OAUTH2_TOKEN')
            user_data = requests.get(
                f"{self.main_url}/api/0.6/user/details.json",
                headers={
                    'Authorization': f"Bearer {self.access_token}",
                    'Content-Type': 'application/json'
                }
            ).json()
        except:
            self.access_token = self.get_access_token()
            user_data = requests.get(
                f"{self.main_url}/api/0.6/user/details.json",
                headers={
                    'Authorization': f"Bearer {self.access_token}",
                    'Content-Type': 'application/json'
                }
            )
            print(f'\033[31m{user_data.content}\033[m')
        self.user_id = user_data['user']['id']
        self.user_name = user_data['user']['display_name']

    def get_oauth2_code(self):
        """
        Obtém o código OAuth2 do usuário.
        """
        code_url = f"{self.main_url}/oauth2/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scopes}"
        print(f"Por favor, acesse o seguinte link para autorizar o aplicativo: {code_url}")
        print("Após autorizar, cole o código no arquivo de configuração e reinicie o serviço.")


    def get_access_token(self, try_count=0):
        """
        Obtém o token de acesso usando o código OAuth2.
        """
        token_url = f"{self.main_url}/oauth2/token"
        data = {
            'grant_type': 'authorization_code',
            'code': self.get_oauth2_code(),
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(token_url, data=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if try_count < 3:
                print("Erro ao obter o token de acesso. Tentando novamente...")
                try_count += 1
                return self.get_access_token(try_count)
            else:
                print("Número máximo de tentativas, excedido.")
        dotenv.set_key(ENVIRONMENT_PATH, 'OSM_OAUTH2_TOKEN', response.json()['access_token'])
        dotenv.set_key(ENVIRONMENT_PATH, 'OSM_OAUTH2_TOKEN_CREATED_AT', str(response.json()['created_at']))
        dotenv.set_key(ENVIRONMENT_PATH, 'OSM_OAUTH2_TOKEN_ID', response.json()['id_token'])
        return response.json()['access_token']
    
    def request(self, endpoint: str, method: str, data: OsmXml) -> requests.Response:
        """
        Faz uma requisição à API do OpenStreetMap.
        """
        url = f"{self.main_url}/api/0.6/{endpoint}"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Content-Type': 'application/xml'
        }
        response = requests.request(method, url, headers=headers, data=str(data))
        return response

    def create_changeset(self, changeset: Changeset) -> OsmXml:
        """
        Cria um changeset no OpenStreetMap.
        """
        data = OsmXml()
        changeset_element = ET.SubElement(data, 'changeset')
        for k,v in changeset.__dict__.items():
            ET.SubElement(changeset_element, 'tag', {'k': k, 'v': v})
        return data

    def create_node(self, node: Node) -> OsmXml:
        """
        Cria um nó no OpenStreetMap.
        """
        data = OsmXml()
        node_element = ET.SubElement(data, 'node', {'changeset': node.changeset_id, 'lat': str(node.lat), 'lon': str(node.lon)})
        for k,v in node.tags.items():
            ET.SubElement(node_element, 'tag', {'k': k, 'v': v})
        return data
    
    def post_new_node(self, node: Node, changeset_id: str | None = None) -> requests.Response:
        """
        Envia um novo nó para o OpenStreetMap.
        """
        if changeset_id:
            node.changeset_id = changeset_id
        else:
            changeset = Changeset(
                author=self.user_name,
                comment=f"Adicionando ponto: {node.tags.get('name', 'Novo ponto')}"
            )
            node.changeset_id = self.request('changeset/create', 'PUT', self.create_changeset(changeset)).text
        
        data = self.create_node(node)
        
        response = self.request(
            endpoint="node/create",
            method="PUT",
            data=data
        )
        return response

if __name__ == "__main__":
    CLIENT_ID = dotenv.get_key(ENVIRONMENT_PATH, 'OSM_CLIENT_ID')
    CLIENT_SECRET = dotenv.get_key(ENVIRONMENT_PATH, 'OSM_CLIENT_SECRET')
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    SCOPES = [
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
    app = OSM(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES)

    print(app.access_token)
