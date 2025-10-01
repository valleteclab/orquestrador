# Guia de Contribuição

## Como Contribuir

Estamos felizes em receber contribuições para o projeto! Aqui estão as formas de contribuir:

### Reportando Bugs
- Use a seção de Issues do GitHub
- Inclua detalhes sobre o ambiente (SO, versão Python, etc.)
- Descreva passos para reproduzir o problema
- Inclua logs relevantes quando possível

### Sugerindo Melhorias
- Abra uma issue descrevendo a melhoria
- Explique o problema que a melhoria resolveria
- Inclua exemplos de uso, se aplicável

### Contribuindo com Código
1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Padrões de Código
- Siga o PEP 8 para estilo Python
- Escreva docstrings para funções e classes
- Inclua comentários para código complexo
- Mantenha funções pequenas e focadas
- Use type hints quando possível

### Processo de Pull Request
- Todos os PRs devem passar nos testes automatizados
- PRs devem ter descrição clara do que foi implementado
- PRs grandes devem ser divididos em commits menores
- Pelo menos uma revisão de código é necessária antes do merge

## Ambiente de Desenvolvimento

### Requisitos
- Python 3.8+
- Redis (para desenvolvimento local)
- Conta na OpenAI (para testes com agentes)
- Instância Chatwoot (pode ser local ou remota)

### Setup Inicial
```bash
# Clone o repositório
git clone [url-do-repositorio]

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp src/config/.env.example src/config/.env
# Edite o arquivo .env com suas configurações

# Execute a aplicação
python src/main.py
```

## Estrutura de Testes

### Testes Unitários
- Localizados em `tests/unit/`
- Testam componentes individuais
- Executados com `pytest tests/unit/`

### Testes de Integração
- Localizados em `tests/integration/`
- Testam interações entre componentes
- Requerem ambiente com Redis e acesso à API

### Testes de API
- Localizados em `tests/api/`
- Testam endpoints da aplicação
- Podem ser executados contra instância local

## Processo de Release

### Versionamento
- Seguimos Semantic Versioning (SemVer)
- Versões estão no formato MAJOR.MINOR.PATCH
- CHANGELOG.md é atualizado a cada release

### Checklist de Release
- [ ] Todos os testes passando
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Tag de versão criada
- [ ] Release publicada no GitHub