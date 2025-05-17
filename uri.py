import re

class URI:
    def __init__(self, *args: str, **kwargs: str):
        self._uri: str = args[0] if args else kwargs.get('uri', '')
        self.protocol: str = kwargs.get('protocol', '')
        self.sub_domain: str = kwargs.get('sub_domain', '')
        self.domain: str = kwargs.get('domain', '')
        self.port: str = kwargs.get('port', '')
        self.path: str = kwargs.get('path', '')
        self.params: dict[str, str] = kwargs.get('params', {})
        self.fragment: str = kwargs.get('fragment', '')
        self._query: str = self._parse_query(self.params)
        self._parse()

    def _parse(self):
        pattern = re.compile(
            r'^(?P<protocol>[a-zA-Z][a-zA-Z\d+\-.]*):\/\/'
            r'(?P<sub_domain>(?:[a-zA-Z\d-]+\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})'
            r'(?::(?P<port>\d+))?'
            r'(?P<path>\/[^\s?]*)?'
            r'(?:\?(?P<query>[^\s#]+))?'
            r'(?:#(?P<fragment>[^\s]+))?$'
        )
        match = pattern.match(self._uri)
        if not match:
            raise ValueError("Invalid URI format")
        
        self.protocol = match.group('protocol')
        self.full_domain = match.group('sub_domain')
        self.sub_domain = self.full_domain.split('.')
        self.domain = '.'.join(self.sub_domain[-2:]) if not self.full_domain.replace('.', '').isdigit() else self.full_domain
        self.sub_domain = '.'.join(self.sub_domain[:-2]) if len(self.sub_domain) > 2 and not self.full_domain.replace('.', '').isdigit() else ''
        self.port = match.group('port') or ''
        self.path = match.group('path') or ''
        self._query = match.group('query') or ''
        self.params = {k:v for k,v in [(kv.split('=')[0], kv.split('=')[1]) for kv in self._query.split('&')]} if self._query else {}
        self.fragment = match.group('fragment') or ''

    def _parse_query(self, params: dict[str, str]) -> str:
        return '&'.join([f'{k}={v}' for k, v in params.items()])
    
    def add_param(self, key: str, value: str):
        self.params[key] = value
        self._query: str = self._parse_query(self.params)

    def remove_param(self, key: str):
        if key in self.params:
            del self.params[key]
        self._query: str = self._parse_query(self.params)

    def root(self) -> str:
        return f'{self.protocol}://{self.full_domain}'

    def __str__(self) -> str:
        uri = f'{self.protocol}://{self.full_domain}'
        if self.port:
            uri += f':{self.port}'
        if self.path:
            uri += self.path
        if self._query:
            uri += f'?{self._query}'
        if self.fragment:
            uri += f'#{self.fragment}'
        return uri

if __name__ == '__main__':
    uri1 = URI('https://master.apis.dev.openstreetmap.org/oauth2/authorize', fragment='test')
    print(uri1)
    uri1.add_param('response_type', 'code')
    uri1.add_param('client_id', 'your_client_id')
    print(uri1.params)