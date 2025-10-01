from src.agents.base_agent import BaseAgent
from typing import List, Dict, Any

class CustomerServiceAgent(BaseAgent):
    """Agente de atendimento ao cliente para WhatsApp"""
    
    def __init__(self, name: str = "CustomerServiceAgent"):
        super().__init__(name, "gpt-3.5-turbo")
        self.system_prompt = """
        Você é um assistente de atendimento ao cliente profissional. 
        Sua função é ajudar os clientes com perguntas, reclamações e solicitações.
        Seja sempre educado, prestativo e objetivo em suas respostas.
        Se não souber a resposta para algo, sugira que o cliente entre em contato 
        com um atendente humano.
        
        Informações importantes:
        - Empresa: [Nome da Empresa]
        - Horário de atendimento: Segunda a sexta, das 9h às 18h
        - Telefone: [Telefone da empresa]
        - Email: [Email da empresa]
        """
        
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processa uma mensagem de atendimento ao cliente"""
        # Preparar o histórico da conversa
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Adicionar histórico da conversa se disponível
        if context and 'conversation_history' in context:
            messages.extend(context['conversation_history'])
        
        # Adicionar a nova mensagem do usuário
        messages.append({"role": "user", "content": message})
        
        # Gerar resposta usando a API OpenAI
        response = self.generate_response(messages)
        
        # Atualizar o histórico da conversa no contexto
        if context is not None:
            if 'conversation_history' not in context:
                context['conversation_history'] = []
            
            context['conversation_history'].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ])
        
        return response

class TechnicalSupportAgent(BaseAgent):
    """Agente de suporte técnico para WhatsApp"""
    
    def __init__(self, name: str = "TechnicalSupportAgent"):
        super().__init__(name, "gpt-4")
        self.system_prompt = """
        Você é um especialista em suporte técnico. 
        Ajude os usuários com problemas técnicos, dúvidas sobre produtos e instruções de uso.
        Seja detalhado e claro em suas explicações.
        Se o problema for complexo, recomende que o usuário entre em contato com o suporte especializado.
        
        Áreas de conhecimento:
        - Instalação de software
        - Configuração de dispositivos
        - Resolução de problemas técnicos
        - Dúvidas sobre funcionalidades
        """
        
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processa uma mensagem de suporte técnico"""
        # Preparar o histórico da conversa
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Adicionar histórico da conversa se disponível
        if context and 'conversation_history' in context:
            messages.extend(context['conversation_history'])
        
        # Adicionar a nova mensagem do usuário
        messages.append({"role": "user", "content": message})
        
        # Gerar resposta usando a API OpenAI
        response = self.generate_response(messages)
        
        # Atualizar o histórico da conversa no contexto
        if context is not None:
            if 'conversation_history' not in context:
                context['conversation_history'] = []
            
            context['conversation_history'].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ])
        
        return response