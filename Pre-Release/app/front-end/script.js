document.getElementById('import-button').addEventListener('click', function() {
    let formData = new FormData(document.getElementById('upload-form'));
    formData.append('file_main', document.getElementById('file-input-main').files[0]);
    formData.append('file_fuel', document.getElementById('file-input-fuel').files[0]);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            alert('Arquivos importados com sucesso!');
            document.getElementById('analyze-button').disabled = false;
            document.getElementById('litros-base-button').disabled = false;
            document.getElementById('custo-base-button').disabled = false;
        } else {
            alert('Erro ao importar os arquivos.');
        }
    });
});
document.getElementById('analyze-button').addEventListener('click', function() {
    fetch('/analyze').then(response => {
        if (response.ok) {
            if (!window.analyzeTab || window.analyzeTab.closed) {
                window.analyzeTab = window.open('http://localhost:8505', '_blank');
            } else {
                window.analyzeTab.focus();
            }
        } else {
            alert('Erro ao iniciar a análise.');
        }
    });
});
document.getElementById('litros-base-button').addEventListener('click', function() {
    fetch('/side_analyze').then(response => {
        if (response.ok) {
            if (!window.sideAnalyzeTab || window.sideAnalyzeTab.closed) {
                window.sideAnalyzeTab = window.open('http://localhost:8506', '_blank');
            } else {
                window.sideAnalyzeTab.focus();
            }
        } else {
            alert('Erro ao iniciar a análise de litros por base.');
        }
    });
});
document.getElementById('custo-base-button').addEventListener('click', function() {
    fetch('/consult').then(response => {
        if (response.ok) {
            if (!window.custoBaseTab || window.custoBaseTab.closed) {
                window.custoBaseTab = window.open('http://localhost:8507', '_blank');
            } else {
                window.custoBaseTab.focus();
            }
        } else {
            alert('Erro ao iniciar a análise de custo por base.');
        }
    });
});
document.getElementById('shutdown-button').addEventListener('click', function() {
    fetch('/shutdown', { method: 'POST' }).then(response => {
        if (response.ok) {
            alert('Sistema fechado com sucesso!');
        } else {
            alert('Erro ao fechar o sistema.');
        }
    });
});