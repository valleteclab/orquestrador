from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Coletor de métricas para o orquestrador de agentes"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_history = deque(maxlen=max_history)
        self.agent_metrics = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': deque(maxlen=100),
            'errors': deque(maxlen=100)
        })
        self.system_metrics = {
            'uptime': datetime.now().isoformat(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'active_sessions': 0
        }
    
    def record_request(self, agent_id: str, success: bool, response_time: float = 0, error: str = None):
        """Registra uma requisição para métricas"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Registrar na história de requisições
            request_record = {
                'timestamp': timestamp,
                'agent_id': agent_id,
                'success': success,
                'response_time': response_time,
                'error': error
            }
            self.request_history.append(request_record)
            
            # Atualizar métricas do agente
            agent_metrics = self.agent_metrics[agent_id]
            agent_metrics['total_requests'] += 1
            if success:
                agent_metrics['successful_requests'] += 1
                agent_metrics['response_times'].append(response_time)
            else:
                agent_metrics['failed_requests'] += 1
                if error:
                    agent_metrics['errors'].append({
                        'timestamp': timestamp,
                        'error': error
                    })
            
            # Atualizar métricas do sistema
            self.system_metrics['total_requests'] += 1
            if success:
                self.system_metrics['successful_requests'] += 1
            else:
                self.system_metrics['failed_requests'] += 1
                
        except Exception as e:
            logger.error(f"Erro ao registrar métrica: {str(e)}")
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Retorna as métricas de um agente específico"""
        try:
            metrics = self.agent_metrics[agent_id].copy()
            
            # Calcular estatísticas
            response_times = list(metrics['response_times'])
            if response_times:
                metrics['avg_response_time'] = sum(response_times) / len(response_times)
                metrics['min_response_time'] = min(response_times)
                metrics['max_response_time'] = max(response_times)
            else:
                metrics['avg_response_time'] = 0
                metrics['min_response_time'] = 0
                metrics['max_response_time'] = 0
            
            # Calcular taxa de sucesso
            total = metrics['total_requests']
            if total > 0:
                metrics['success_rate'] = metrics['successful_requests'] / total
            else:
                metrics['success_rate'] = 0
            
            return dict(metrics)
        except Exception as e:
            logger.error(f"Erro ao recuperar métricas do agente {agent_id}: {str(e)}")
            return {}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Retorna as métricas gerais do sistema"""
        try:
            metrics = self.system_metrics.copy()
            
            # Calcular tempo de atividade
            uptime_str = metrics['uptime']
            uptime_dt = datetime.fromisoformat(uptime_str)
            uptime_seconds = (datetime.now() - uptime_dt).total_seconds()
            metrics['uptime_seconds'] = uptime_seconds
            
            # Calcular taxa de sucesso geral
            total = metrics['total_requests']
            if total > 0:
                metrics['success_rate'] = metrics['successful_requests'] / total
            else:
                metrics['success_rate'] = 0
            
            # Adicionar estatísticas recentes
            recent_requests = list(self.request_history)[-100:]  # Últimas 100 requisições
            if recent_requests:
                recent_success = sum(1 for r in recent_requests if r['success'])
                metrics['recent_success_rate'] = recent_success / len(recent_requests)
            else:
                metrics['recent_success_rate'] = 0
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao recuperar métricas do sistema: {str(e)}")
            return {}
    
    def get_agent_performance_ranking(self) -> List[Dict[str, Any]]:
        """Retorna um ranking de desempenho dos agentes"""
        try:
            ranking = []
            for agent_id, metrics in self.agent_metrics.items():
                total = metrics['total_requests']
                if total > 0:
                    success_rate = metrics['successful_requests'] / total
                    response_times = list(metrics['response_times'])
                    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                    
                    ranking.append({
                        'agent_id': agent_id,
                        'success_rate': success_rate,
                        'total_requests': total,
                        'avg_response_time': avg_response_time,
                        'failed_requests': metrics['failed_requests']
                    })
            
            # Ordenar por taxa de sucesso (descendente) e tempo de resposta (ascendente)
            ranking.sort(key=lambda x: (-x['success_rate'], x['avg_response_time']))
            return ranking
        except Exception as e:
            logger.error(f"Erro ao gerar ranking de desempenho: {str(e)}")
            return []
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna os erros recentes de todos os agentes"""
        try:
            all_errors = []
            for agent_id, metrics in self.agent_metrics.items():
                for error in metrics['errors']:
                    error_record = error.copy()
                    error_record['agent_id'] = agent_id
                    all_errors.append(error_record)
            
            # Ordenar por timestamp (mais recente primeiro)
            all_errors.sort(key=lambda x: x['timestamp'], reverse=True)
            return all_errors[:limit]
        except Exception as e:
            logger.error(f"Erro ao recuperar erros recentes: {str(e)}")
            return []
    
    def reset_metrics(self):
        """Reseta todas as métricas (para testes ou manutenção)"""
        try:
            self.request_history.clear()
            self.agent_metrics.clear()
            self.system_metrics.update({
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'active_sessions': 0
            })
            logger.info("Métricas resetadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao resetar métricas: {str(e)}")