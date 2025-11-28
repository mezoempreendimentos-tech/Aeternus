# backend/game/engines/time/manager.py
import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Callable, List
from .calendar import GameDate, GAME_SECONDS_PER_DAY, MONTHS_PER_YEAR, DAYS_PER_MONTH, TIME_MULTIPLIER

logger = logging.getLogger(__name__)

STATE_FILE = Path("data/gamestate.json")

class TimeEngine:
    """
    O Relógio do Mundo.
    Agora com persistência: o tempo avança mesmo com o servidor offline.
    """
    def __init__(self):
        # Momento exato que ESTA sessão do servidor iniciou
        self.session_start_real_time = time.time()
        
        # O acumulado de segundos de jogo até o momento do boot
        self.base_game_seconds = 0
        
        # Ano inicial padrão (se for o primeiro boot da história)
        self.game_year_offset = 1000 
        
        self.combat_subscribers: List[Callable] = []
        self.global_subscribers: List[Callable] = []
        self._running = False

    def load_state(self):
        """
        Recupera o tempo perdido.
        Calcula quanto tempo passou offline e avança o relógio.
        """
        if not STATE_FILE.exists():
            logger.info("TimeEngine: Nenhum estado salvo. Iniciando no Ano 1000.")
            self.base_game_seconds = 0
            return

        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                
            last_game_seconds = data.get("total_game_seconds", 0)
            last_real_timestamp = data.get("real_timestamp", time.time())
            
            # Quanto tempo o servidor ficou desligado?
            offline_real_seconds = time.time() - last_real_timestamp
            
            # Converte tempo offline em tempo de jogo
            offline_game_seconds = offline_real_seconds * TIME_MULTIPLIER
            
            # Define o novo ponto de partida
            self.base_game_seconds = last_game_seconds + offline_game_seconds
            
            logger.info(f"TimeEngine: Estado carregado. O mundo avançou {offline_game_seconds:.2f}s (jogo) enquanto offline.")
            
        except Exception as e:
            logger.error(f"TimeEngine: Erro ao carregar save: {e}")
            self.base_game_seconds = 0

    def save_state(self):
        """Congela o momento atual no disco."""
        try:
            data = {
                "total_game_seconds": self._get_total_game_seconds(),
                "real_timestamp": time.time(),
                "last_date_string": str(self.get_current_date()) # Apenas para debug humano
            }
            
            with open(STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("TimeEngine: Tempo salvo com sucesso.")
        except Exception as e:
            logger.error(f"TimeEngine: Erro ao salvar estado: {e}")

    def _get_total_game_seconds(self) -> float:
        """Calcula o total absoluto de segundos desde o Big Bang do jogo."""
        # Tempo decorrido NESTA sessão real
        current_session_delta = time.time() - self.session_start_real_time
        
        # Converte para tempo de jogo
        game_delta = current_session_delta * TIME_MULTIPLIER
        
        # Soma ao que já tínhamos antes do boot
        return self.base_game_seconds + game_delta

    def get_current_date(self) -> GameDate:
        """Traduz os segundos totais em uma Data (Ano, Mês, Dia)."""
        total_game_seconds = self._get_total_game_seconds()
        
        # Cálculos de calendário
        total_days = int(total_game_seconds // GAME_SECONDS_PER_DAY)
        current_second_in_day = int(total_game_seconds % GAME_SECONDS_PER_DAY)
        
        years = total_days // (MONTHS_PER_YEAR * DAYS_PER_MONTH)
        days_remaining = total_days % (MONTHS_PER_YEAR * DAYS_PER_MONTH)
        
        months = days_remaining // DAYS_PER_MONTH
        day_of_month = days_remaining % DAYS_PER_MONTH
        
        hour = current_second_in_day // 3600
        minute = (current_second_in_day % 3600) // 60
        
        return GameDate(
            year=self.game_year_offset + years,
            month=months + 1,
            day=day_of_month + 1,
            hour=hour,
            minute=minute
        )

    async def start_loop(self):
        """Inicia os loops."""
        self.load_state() # <--- Carrega antes de iniciar
        self._running = True
        
        # Salva o estado periodicamente (auto-save a cada 5 min) para evitar perda em crash
        asyncio.create_task(self._auto_save_loop())
        asyncio.create_task(self._combat_tick_loop())
        asyncio.create_task(self._global_tick_loop())

    async def _auto_save_loop(self):
        while self._running:
            await asyncio.sleep(300) # 5 minutos
            self.save_state()

    # ... (Mantenha _combat_tick_loop e _global_tick_loop iguais ao anterior) ...
    
    async def _combat_tick_loop(self):
        while self._running:
            start_time = time.time()
            for callback in self.combat_subscribers:
                try:
                    # Verifica se é corrotina antes de await
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"Erro Combat Tick: {e}")
            
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, 2.0 - elapsed))

    async def _global_tick_loop(self):
        while self._running:
            start_time = time.time()
            current_date = self.get_current_date()
            
            # self._check_special_events(current_date)
            
            for callback in self.global_subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(current_date)
                    else:
                        callback(current_date)
                except Exception as e:
                    logger.error(f"Erro Global Tick: {e}")
            
            elapsed = time.time() - start_time
            await asyncio.sleep(max(0, 10.0 - elapsed))
            
    def register_combat_subscriber(self, callback):
        self.combat_subscribers.append(callback)

    def register_global_subscriber(self, callback):
        self.global_subscribers.append(callback)