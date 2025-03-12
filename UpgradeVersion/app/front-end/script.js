document.getElementById('import-button').addEventListener('click', () => {
    const formData = new FormData(document.getElementById('upload-form'));
    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            document.getElementById('analyze-button').disabled = false;
            document.getElementById('litros-base-button').disabled = false;
            document.getElementById('custo-base-button').disabled = false;
            document.getElementById('paynotes-button').disabled = false;
            alert('Arquivos importados com sucesso!');
        } else {
            alert('Erro ao importar os arquivos.');
        }
    });
});

document.getElementById('analyze-button').addEventListener('click', () => {
    fetch('/analyze').then(response => {
        if (response.ok) {
            alert('Análise iniciada.');
        } else {
            alert('Erro ao iniciar a análise.');
        }
    });
});

document.getElementById('litros-base-button').addEventListener('click', () => {
    fetch('/side_analyze').then(response => {
        if (response.ok) {
            alert('Análise de litros base iniciada.');
        } else {
            alert('Erro ao iniciar a análise de litros base.');
        }
    });
});

document.getElementById('custo-base-button').addEventListener('click', () => {
    fetch('/consult').then(response => {
        if (response.ok) {
            alert('Consulta de custo base iniciada.');
        } else {
            alert('Erro ao iniciar a consulta de custo base.');
        }
    });
});

document.getElementById('paynotes-button').addEventListener('click', () => {
    fetch('/paynotes').then(response => {
        if (response.ok) {
            alert('Análise de notas de pagamento iniciada.');
        } else {
            alert('Erro ao iniciar a análise de notas de pagamento.');
        }
    });
});

document.getElementById('shutdown-button').addEventListener('click', () => {
    fetch('/shutdown', { method: 'POST' }).then(response => {
        if (response.ok) {
            alert('Sistema limpo e fechado.');
        } else {
            alert('Erro ao limpar e fechar o sistema.');
        }
    });
});
