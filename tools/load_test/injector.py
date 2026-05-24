import sys
import time
import uuid
import shutil
import argparse
from pathlib import Path

def launch_load_test(source_pdf: str, num_copies: int, target_inbox: str):
    source_path = Path(source_pdf)
    inbox_path = Path(target_inbox)
    
    if not source_path.exists():
        print(f"[ERROR] El PDF de control especificado no existe: {source_path.absolute()}")
        sys.exit(1)
        
    if not inbox_path.exists():
        print(f"[INFO] Creando directorio Inbox objetivo: {inbox_path.absolute()}")
        inbox_path.mkdir(parents=True, exist_ok=True)
        
    print("=" * 65)
    print("        SOTA SRE LOAD INJECTOR - INICIALIZANDO FASE 8B")
    print("=" * 65)
    print(f"PDF Origen:       {source_path.name} ({source_path.stat().st_size / 1024:.1f} KB)")
    print(f"Copias a emitir:  {num_copies}")
    print(f"Destino (Inbox):  {inbox_path.absolute()}")
    print("-" * 65)
    
    # Registro del timestamp base de alta precisión
    start_time = time.time()
    print(f"[TIMESTAMP INICIO] {start_time} (Epoch Unix)")
    print("[EJECUCIÓN] Inyectando ráfaga concurrente en File System...")
    
    generated_files = []
    
    for i in range(1, num_copies + 1):
        # SOTA: Mutación de nombre vía UUID v4 para evitar colisiones lógicas
        unique_id = uuid.uuid4().hex[:8]
        templated_name = f"LOAD_TEST_{unique_id}_{source_path.stem}.pdf"
        destination = inbox_path / templated_name
        
        try:
            shutil.copy2(str(source_path), str(destination))
            generated_files.append(destination)
        except IOError as err:
            print(f"[CRÍTICO] Fallo de I/O escribiendo copia {i}: {err}")
            sys.exit(1)
            
    end_injection_time = time.time()
    delta_injection = end_injection_time - start_time
    
    print("-" * 65)
    print("[OK] Inyección completada exitosamente.")
    print(f"Tiempo de ráfaga: {delta_injection:.4f} segundos.")
    print(f"Throughput de Ingesta Local: {num_copies / (delta_injection if delta_injection > 0 else 0.001):.2f} docs/sec")
    print("=" * 65)
    print("[MÉTRICA COMPORTAMIENTO] Monitorea la carpeta con el siguiente comando:")
    print(f"  watch -n 1 'ls -la {target_inbox}'")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inyector de carga asíncrono/FS para validación de breaking points.")
    parser.add_argument("--source", type=str, default="input.pdf", help="Ruta al PDF real que se clonará.")
    parser.add_argument("--copies", type=int, default=5, help="Número de documentos simultáneos a inyectar.")
    parser.add_argument("--inbox", type=str, default="data/inbox", help="Ruta física a la carpeta data/inbox.")
    
    args = parser.parse_args()
    launch_load_test(source_pdf=args.source, num_copies=args.copies, target_inbox=args.inbox)