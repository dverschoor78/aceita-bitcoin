document.addEventListener("DOMContentLoaded", () => {
  // Inicializar o mapa do OpenStreetMap
  const map = L.map('osmMap').setView([-23.55052, -46.633308], 13); // São Paulo como centro inicial

  // Adicionar camada de tiles do OSM
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Adicionar marcador temporário
  const marker = L.marker([-23.55052, -46.633308], { draggable: true }).addTo(map);

  // Atualizar coordenadas ao mover o marcador
  marker.on('moveend', (event) => {
    const { lat, lng } = event.target.getLatLng();
    console.log(`Nova posição: Latitude ${lat}, Longitude ${lng}`);
  });

  // Botão de salvar alterações
  const saveChangesBtn = document.getElementById('saveChangesBtn');
  saveChangesBtn.addEventListener('click', () => {
    const { lat, lng } = marker.getLatLng();
    if (lat && lng) {
        alert(`Salvando alterações: Latitude ${lat}, Longitude ${lng}`);
        // Enviar os dados para o backend
    } else {
        alert('Erro: Coordenadas inválidas.');
    }
  });

  // Botão de cancelar
  const cancelBtn = document.getElementById('cancelBtn');
  cancelBtn.addEventListener('click', () => {
    alert('Alterações canceladas.');
    // Implementar lógica adicional, se necessário
  });
});