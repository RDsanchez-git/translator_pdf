import sqlite3
from pathlib import Path

db_path = Path('reports/regression_test/telemetry.db')
conn = sqlite3.connect(str(db_path))

print('=' * 70)
print('VALIDACION DE COMPLETITUD - Task 1.1.2')
print('=' * 70)

# 1. Verificar que execution_id es consistente (todos iguales)
exec_ids = conn.execute('SELECT DISTINCT execution_id FROM stage_execution_records').fetchall()
print('\n1. Execution IDs unicos:', len(exec_ids))
if len(exec_ids) == 1:
    print('   [OK] Todos los stages comparten execution_id:', exec_ids[0][0][:16], '...')
else:
    print('   [FAIL] ERROR: Encontrados', len(exec_ids), 'execution_ids diferentes')

# 2. Verificar que no hay NULLs en campos requeridos
null_checks = conn.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN execution_id IS NULL THEN 1 ELSE 0 END) as null_exec_id,
        SUM(CASE WHEN stage_name IS NULL THEN 1 ELSE 0 END) as null_stage_name,
        SUM(CASE WHEN stage_index IS NULL THEN 1 ELSE 0 END) as null_stage_index,
        SUM(CASE WHEN latency_sec IS NULL THEN 1 ELSE 0 END) as null_latency,
        SUM(CASE WHEN input_type IS NULL THEN 1 ELSE 0 END) as null_input_type,
        SUM(CASE WHEN output_type IS NULL THEN 1 ELSE 0 END) as null_output_type,
        SUM(CASE WHEN status IS NULL THEN 1 ELSE 0 END) as null_status,
        SUM(CASE WHEN timestamp IS NULL THEN 1 ELSE 0 END) as null_timestamp
    FROM stage_execution_records
''').fetchone()

print('\n2. Verificacion de NULLs en campos requeridos:')
print('   Total de registros:', null_checks[0])
fields = ['execution_id', 'stage_name', 'stage_index', 'latency_sec', 
          'input_type', 'output_type', 'status', 'timestamp']
all_ok = True
for i, field in enumerate(fields, 1):
    null_count = null_checks[i]
    if null_count == 0:
        print('  ', field.ljust(20), '[OK] 0 NULLs')
    else:
        print('  ', field.ljust(20), '[FAIL]', null_count, 'NULLs')
        all_ok = False

# 3. Verificar timestamps validos (ISO 8601)
timestamps = conn.execute('SELECT timestamp FROM stage_execution_records').fetchall()
print('\n3. Verificacion de timestamps (ISO 8601):')
valid_timestamps = 0
for ts in timestamps:
    try:
        if 'T' in ts[0] and '-' in ts[0] and ':' in ts[0]:
            valid_timestamps += 1
    except Exception:
        pass
print('   Timestamps validos:', str(valid_timestamps) + '/' + str(len(timestamps)))
if valid_timestamps == len(timestamps):
    print('   [OK] Todos los timestamps tienen formato ISO 8601')
else:
    print('   [FAIL]', len(timestamps) - valid_timestamps, 'timestamps con formato invalido')

# 4. Verificar metadata (document_id presente en EXTRACTION y TOPOLOGY_EVALUATION)
metadata_check = conn.execute('''
    SELECT stage_name, metadata 
    FROM stage_execution_records 
    WHERE stage_index IN (0, 1)
''').fetchall()

print('\n4. Verificacion de metadata (document_id en stages 0 y 1):')
docs_with_metadata = sum(1 for _, meta in metadata_check if meta and 'document_id' in meta)
print('   Stages con document_id en metadata:', str(docs_with_metadata) + '/' + str(len(metadata_check)))
if docs_with_metadata == len(metadata_check):
    print('   [OK] Todos los stages de documento tienen document_id en metadata')
else:
    print('   [FAIL]', len(metadata_check) - docs_with_metadata, 'stages sin document_id')

# 5. Resumen de latencias por stage
print('\n5. Resumen de latencias por stage:')
latency_stats = conn.execute('''
    SELECT 
        stage_name,
        COUNT(*) as count,
        MIN(latency_sec) as min_lat,
        MAX(latency_sec) as max_lat,
        AVG(latency_sec) as avg_lat
    FROM stage_execution_records
    GROUP BY stage_name
    ORDER BY MIN(stage_index)
''').fetchall()

header = '   ' + 'Stage'.ljust(25) + 'Count'.ljust(8) + 'Min (s)'.ljust(12) + 'Max (s)'.ljust(12) + 'Avg (s)'.ljust(12)
print(header)
print('   ' + '-' * 69)
for stage_name, count, min_lat, max_lat, avg_lat in latency_stats:
    row = '   ' + stage_name.ljust(25) + str(count).ljust(8)
    row += format(min_lat, '.4f').ljust(12)
    row += format(max_lat, '.4f').ljust(12)
    row += format(avg_lat, '.4f').ljust(12)
    print(row)

# 6. Veredicto final
print('\n' + '=' * 70)
if len(exec_ids) == 1 and all_ok and valid_timestamps == len(timestamps) and docs_with_metadata == len(metadata_check):
    print('VEREDICTO: [OK] PASS - Datos completos y consistentes')
else:
    print('VEREDICTO: [FAIL] FAIL - Inconsistencias detectadas')
print('=' * 70)

conn.close()
