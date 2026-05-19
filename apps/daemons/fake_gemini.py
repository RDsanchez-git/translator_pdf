import random
import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# SOTA: Logging con formato estricto para correlación
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fake_gemini")

app = FastAPI(title="Fake Gemini Chaos Server")

# ==========================================
# ESTADO DE CAOS (RNG Aislado y Atomics)
# ==========================================
class ChaosConfig:
    def __init__(self):
        self.global_seed: str | None = None  # SOTA: Semilla base para reproducibilidad
        self.latency_min_ms: int = 100
        self.latency_max_ms: int = 500
        self.error_500_prob: float = 0.0
        self.error_429_prob: float = 0.0
        self.hang_prob: float = 0.0
        self.malformed_prob: float = 0.0
        self.chunked_drop_prob: float = 0.0  # SOTA: Vector de TCP drop mid-stream
        
        self.max_active_hangs: int = 50 
        self.max_concurrency: int = 100
        
        # SOTA: Locks explícitos para backpressure dinámico
        self._metrics_lock = asyncio.Lock()
        self.active_requests: int = 0

chaos_state = ChaosConfig()

class Metrics:
    def __init__(self):
        self.total_requests: int = 0
        self.active_hangs: int = 0
        self.count_500: int = 0
        self.count_429: int = 0
        self.count_malformed: int = 0
        self.count_hangs: int = 0
        self.count_chunked_drops: int = 0

metrics = Metrics()

class ChaosMutation(BaseModel):
    latency_min_ms: int | None = None
    latency_max_ms: int | None = None
    error_500_prob: float | None = None
    error_429_prob: float | None = None
    hang_prob: float | None = None
    malformed_prob: float | None = None
    chunked_drop_prob: float | None = None
    seed: int | None = None  # SOTA: Reproducibilidad

# ==========================================
# ENDPOINTS DE CONTROL (SRE)
# ==========================================
@app.get("/health")
def health_check():
    return {"status": "ok", "metrics": metrics.__dict__}

@app.post("/_chaos/config")
async def mutate_chaos(mutation: ChaosMutation):
    """Mutación con re-seeding global."""
    if mutation.seed is not None: 
        chaos_state.global_seed = str(mutation.seed)
        logger.warning(f"CHAOS_SEED_SET: {chaos_state.global_seed}")
        
    if mutation.latency_min_ms is not None:
        chaos_state.latency_min_ms = mutation.latency_min_ms
    if mutation.latency_max_ms is not None:
        chaos_state.latency_max_ms = mutation.latency_max_ms
    if mutation.error_500_prob is not None:
        chaos_state.error_500_prob = mutation.error_500_prob
    if mutation.error_429_prob is not None:
        chaos_state.error_429_prob = mutation.error_429_prob
    if mutation.hang_prob is not None:
        chaos_state.hang_prob = mutation.hang_prob
    if mutation.malformed_prob is not None:
        chaos_state.malformed_prob = mutation.malformed_prob
    if mutation.chunked_drop_prob is not None:
        chaos_state.chunked_drop_prob = mutation.chunked_drop_prob
    
    return {"status": "chaos_updated"}

# ==========================================
# ENDPOINT UPSTREAM (Mock API Gemini)
# ==========================================
@app.post("/v1beta/models/{model}:generateContent")
async def generate_content(model: str, request: Request):
    exec_id = request.headers.get("x-execution-id", "unknown_exec")
    worker_id = request.headers.get("x-worker-id", "unknown_worker")
    
    # SOTA: Backpressure Dinámico Atómico (Reemplaza al Semaphore inmutable)
    async with chaos_state._metrics_lock:
        metrics.total_requests += 1
        if chaos_state.active_requests >= chaos_state.max_concurrency:
            logger.warning(f"FAKE_GEMINI_SATURATED_503 exec_id={exec_id}")
            return JSONResponse(status_code=503, content={"error": {"message": "Service Unavailable (Chaos Overload)"}})
        chaos_state.active_requests += 1

    try:
        logger.info(f"REQUEST_RECEIVED exec_id={exec_id} worker_id={worker_id}")

        # SOTA: Generación de RNG local y determinístico por request
        if chaos_state.global_seed:
            deterministic_seed = f"{chaos_state.global_seed}:{exec_id}"
            request_rng = random.Random(deterministic_seed)
        else:
            request_rng = random.Random()

        p_500 = request_rng.random()
        p_429 = request_rng.random()
        p_hang = request_rng.random()
        p_malformed = request_rng.random()
        p_chunked = request_rng.random()

        # 1. Inyección de Hang (Black Hole TCP)
        if p_hang < chaos_state.hang_prob:
            async with chaos_state._metrics_lock:
                if metrics.active_hangs < chaos_state.max_active_hangs:
                    metrics.active_hangs += 1
                    metrics.count_hangs += 1
                    can_hang = True
                else:
                    can_hang = False
            
            if can_hang:
                logger.warning(f"HANG_INJECTED exec_id={exec_id} worker_id={worker_id}")
                try:
                    await asyncio.sleep(86400)
                finally:
                    async with chaos_state._metrics_lock:
                        metrics.active_hangs -= 1
            else:
                logger.info(f"HANG_LIMIT_REACHED exec_id={exec_id}")

        # 2. Corrupción de Transferencia (Partial Streaming Drop)
        if p_chunked < chaos_state.chunked_drop_prob:
            async with chaos_state._metrics_lock:
                metrics.count_chunked_drops += 1
            logger.critical(f"CHUNKED_DROP_INJECTED exec_id={exec_id}")
            
            async def broken_stream():
                yield b'{"candidates": [{"content": {"parts": [{"text": "[TRANSL'
                await asyncio.sleep(0.5)
                # Esto fuerza un cierre abrupto de la conexión TCP a la mitad
                raise RuntimeError("SOTA: Socket dropped unexpectedly mid-stream")
            return StreamingResponse(broken_stream(), media_type="application/json")

        # 3. Inyección de Latencia
        latency_ms = request_rng.randint(chaos_state.latency_min_ms, chaos_state.latency_max_ms)
        await asyncio.sleep(latency_ms / 1000.0)

        # 4. Inyección de Errores HTTP
        if p_500 < chaos_state.error_500_prob:
            async with chaos_state._metrics_lock:
                metrics.count_500 += 1
            logger.warning(f"500_INJECTED exec_id={exec_id}")
            return JSONResponse(status_code=500, content={"error": {"message": "Internal Server Error (Chaos)"}})
        
        if p_429 < chaos_state.error_429_prob:
            async with chaos_state._metrics_lock:
                metrics.count_429 += 1
            logger.warning(f"429_INJECTED exec_id={exec_id}")
            return JSONResponse(status_code=429, content={"error": {"message": "Quota Exceeded (Chaos)"}})

        # 5. Inyección de Corrupción de Payload (Malformed JSON)
        if p_malformed < chaos_state.malformed_prob:
            async with chaos_state._metrics_lock:
                metrics.count_malformed += 1
            logger.warning(f"MALFORMED_INJECTED exec_id={exec_id}")
            return Response(content='{"candidates": [{"content": {"pa', media_type="application/json")

        # 6. Respuesta Feliz
        try:
            payload = await request.json()
            user_text = payload["contents"][0]["parts"][0]["text"]
            mock_translation = f"[TRANSLATED_MOCK] {user_text[:30]}..."
        except Exception:
            mock_translation = "[TRANSLATED_MOCK_FALLBACK]"

        return {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": mock_translation}],
                        "role": "model"
                    },
                    "finishReason": "STOP"
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 15,
                "totalTokenCount": 25
            }
        }

    finally:
        # SOTA: Liberación segura atómica del recurso de backpressure
        async with chaos_state._metrics_lock:
            chaos_state.active_requests -= 1