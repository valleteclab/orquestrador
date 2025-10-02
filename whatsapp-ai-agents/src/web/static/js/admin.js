// Funções JavaScript para o painel administrativo

// Inicialização quando o documento estiver pronto
$(document).ready(function() {
    // Ativar tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Ativar sidebar toggle
    $('.sidebar-toggle').on('click', function() {
        $('.main-sidebar').toggleClass('sidebar-open');
    });
    
    // Ativar cards expansíveis
    $('[data-widget="collapse"]').on('click', function() {
        var $this = $(this);
        var $parent = $this.closest('.card');
        var $body = $parent.find('.card-body');
        
        $body.slideToggle();
        $this.toggleClass('fa-minus fa-plus');
    });
});

// Função para carregar logs em tempo real
function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logContainer = document.getElementById('log-container');
            if (logContainer) {
                logContainer.innerHTML = data.logs.map(log => 
                    `<div class="log-entry">${log}</div>`
                ).join('');
                
                // Rolar para o final
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        })
        .catch(error => console.error('Erro ao carregar logs:', error));
}

// Função para carregar estatísticas
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Atualizar elementos com as estatísticas
            document.querySelectorAll('[data-stat]').forEach(element => {
                const statKey = element.getAttribute('data-stat');
                if (data[statKey] !== undefined) {
                    element.textContent = data[statKey];
                }
            });
        })
        .catch(error => console.error('Erro ao carregar estatísticas:', error));
}

// Função para testar um agente
function testAgent(agentId) {
    // Esta função será implementada no template específico
    console.log('Testando agente:', agentId);
}

// Função para enviar mensagem de teste
function sendTestMessage() {
    // Esta função será implementada no template específico
    console.log('Enviando mensagem de teste');
}

// Função para editar agente
function editAgent(agentId) {
    alert('Funcionalidade de edição em desenvolvimento. Agente: ' + agentId);
}

// Função para excluir agente
function deleteAgent(agentId) {
    if (confirm('Tem certeza que deseja excluir o agente ' + agentId + '?')) {
        alert('Funcionalidade de exclusão em desenvolvimento. Agente: ' + agentId);
    }
}

// Carregar logs e estatísticas a cada 5 segundos
if (document.getElementById('log-container') || document.querySelector('[data-stat]')) {
    setInterval(() => {
        loadLogs();
        loadStats();
    }, 5000);
}

// Função para salvar configurações de agente
function saveAgentConfig(agentId, config) {
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
            alert('Erro ao salvar configurações');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar configurações');
    });
}