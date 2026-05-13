import json
from pathlib import Path
from runtime.engine import run_pipeline

# SOTA: Configuración del entorno de estrés
CLEAN_CACHE_PER_DOCUMENT = True  # Flag para tests de warm/cold cache
CORPUS_DIR = Path("tests/corpus")
OUTPUT_DIR = Path("tests/output")
REPORT_FILE = Path("tests/stress_report.json")

def run_stress_tests():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(CORPUS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️ El corpus está vacío. Coloca PDFs complejos en: {CORPUS_DIR}")
        return

    print(f"🚀 Iniciando Stress Test SOTA sobre {len(pdf_files)} documentos...")
    report = {
        "total_documents": len(pdf_files),
        "success_rate": 0.0,
        "auto_healed_count": 0,
        "failed_count": 0,
        "results": {}
    }

    success_count = 0

    for pdf in pdf_files:
        print(f"\n[{pdf.name}] Ingestando al pipeline...")
        # SOTA: Aislamiento estricto de outputs
        out_name = str(OUTPUT_DIR / f"translated_{pdf.name}")


        try:
            metrics = run_pipeline(str(pdf), out_name)
            report["results"][pdf.name] = metrics
            
            if metrics.get("status") == "success":
                success_count += 1
                if metrics.get("attempts", 1) > 1:
                    report["auto_healed_count"] += 1
                    print(f"✅ [{pdf.name}] COMPILADO (Auto-curado en {metrics['attempts']} intentos)")
                else:
                    print(f"✅ [{pdf.name}] COMPILADO (Perfecto al 1er intento)")
            else:
                report["failed_count"] += 1
                print(f"❌ [{pdf.name}] FALLO TERMINAL: {metrics.get('error_type')}")
                
        except Exception as e:
            report["failed_count"] += 1
            report["results"][pdf.name] = {"status": "crash", "stderr": str(e)}
            print(f"❌ [{pdf.name}] CRASH DEL MOTOR: {str(e)}")

    report["success_rate"] = round((success_count / len(pdf_files)) * 100, 2) if pdf_files else 0.0

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print("\n📊 STRESS TEST COMPLETADO.")
    print(f"-> Compile Success Rate : {report['success_rate']}%")
    print(f"-> Activaciones LogParser: {report['auto_healed_count']}")
    print(f"-> Reporte persistido en : {REPORT_FILE}")

if __name__ == "__main__":
    run_stress_tests()