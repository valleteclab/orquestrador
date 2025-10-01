// Funcionalidades do painel administrativo

// Função para carregar logs em tempo real
function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            if (logsContainer) {
                logsContainer.innerHTML = data.logs.join('\n');
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }
        })
        .catch(error => console.error('Erro ao carregar logs:', error));
}

// Função para testar um agente
function testAgent(agentId) {
    const message = document.getElementById(`test-message-${agentId}`).value;
    if (!message) {
        alert('Por favor, digite uma mensagem para testar.');
        return;
    }
    
    fetch('/api/test-agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            agent_id: agentId,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`test-response-${agentId}`).innerText = data.response;
    })
    .catch(error => {
        console.error('Erro ao testar agente:', error);
        document.getElementById(`test-response-${agentId}`).innerText = 'Erro ao testar agente.';
    });
}

// Função para salvar configurações do agente
function saveAgentConfig(agentId) {
    const form = document.getElementById(`agent-form-${agentId}`);
    const formData = new FormData(form);
    
    const config = {};
    for (let [key, value] of formData.entries()) {
        config[key] = value;
    }
    
    fetch('/api/agent-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            agent_id: agentId,
            config: config
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Configurações salvas com sucesso!');
        } else {
            alert('Erro ao salvar configurações.');
        }
    })
    .catch(error => {
        console.error('Erro ao salvar configurações:', error);
        alert('Erro ao salvar configurações.');
    });
}

// Função para carregar estatísticas
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-conversations').innerText = data.total_conversations;
            document.getElementById('total-messages').innerText = data.total_messages;
            document.getElementById('avg-response-time').innerText = data.avg_response_time;
            document.getElementById('satisfaction-rate').innerText = data.satisfaction_rate;
        })
        .catch(error => console.error('Erro ao carregar estatísticas:', error));
}

// Carregar logs a cada 5 segundos
setInterval(loadLogs, 5000);

// Carregar estatísticas a cada 30 segundos
setInterval(loadStats, 30000);

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    loadLogs();
    loadStats();
});