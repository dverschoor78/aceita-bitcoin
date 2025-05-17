document.addEventListener('DOMContentLoaded', function() {
    const cadastroForm = document.getElementById('cadastroForm');
    const goToHomeBtn = document.getElementById('goToHomeBtn');
    const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));

    cadastroForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('nome', document.getElementById('nomeEstabelecimento').value);
        formData.append('tipo', document.getElementById('tipoEstabelecimento').value);
        formData.append('endereco', document.getElementById('endereco').value);
        formData.append('latitude', document.getElementById('latitude').value);
        formData.append('longitude', document.getElementById('longitude').value);
        formData.append('email', document.getElementById('email').value);
        formData.append('telefone', document.getElementById('telefone').value);
        formData.append('website', document.getElementById('website').value);
        formData.append('observacoes', document.getElementById('observacoes').value);
        formData.append('aceita_lightning', document.getElementById('acceptsLightning').checked);
        formData.append('aceita_onchain', document.getElementById('acceptsOnchain').checked);
        formData.append('aceita_contactless', document.getElementById('acceptsLightningContactless').checked);

        const logoFile = document.getElementById('logoEstabelecimento').files[0];
        if (logoFile) {
            formData.append('logo', logoFile);
        }

        try {
            const response = await fetch('/api/estabelecimentos', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                confirmationModal.show();
                cadastroForm.reset();
                document.getElementById('checkDate').value = new Date().toISOString().split('T')[0];
            } else {
                console.log('Erro: ' + result.message);
            }
        } catch (error) {
            console.error('Erro ao enviar formulário:', error);
        }
    });

    goToHomeBtn.addEventListener('click', function() {
        window.location.href = "/";
    });
});
