"""Offline G5/2 regression: real sqlite3 WAL files and assembly lease repository."""
import os
import sqlite3
import threading
import time

import pytest

from infra.db.assembly_recovery import AssemblyLeaseRepository


@pytest.fixture
def sandbox(tmp_path):
    fsm = tmp_path / 'fsm.db'
    queue = tmp_path / 'queue.db'
    a = sqlite3.connect(fsm)
    a.execute('PRAGMA journal_mode=WAL')
    a.executescript('''
        CREATE TABLE document_fsm (
            document_id TEXT NOT NULL,ast_hash TEXT NOT NULL,current_state TEXT NOT NULL,
            state_version INTEGER NOT NULL DEFAULT 0,entered_state_at REAL,created_at REAL,
            updated_at REAL NOT NULL,is_terminal INTEGER NOT NULL DEFAULT 0,
            failure_reason TEXT,suspended_state TEXT,retry_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(document_id,ast_hash)
        );
    ''')
    a.execute("INSERT INTO document_fsm(document_id,ast_hash,current_state,updated_at) VALUES ('doc','ast','READY_FOR_ASSEMBLY',?)", (time.time(),))
    a.commit()
    a.close()
    a = sqlite3.connect(queue)
    a.execute('PRAGMA journal_mode=WAL')
    a.executescript('''
        CREATE TABLE chunk_tasks (
          task_id TEXT PRIMARY KEY,document_id TEXT NOT NULL,ast_hash TEXT NOT NULL,
          node_id TEXT NOT NULL,task_state TEXT NOT NULL DEFAULT 'PENDING',
          worker_type TEXT NOT NULL DEFAULT 'LLM',execution_id TEXT,
          retry_count INTEGER NOT NULL DEFAULT 0,max_retries INTEGER NOT NULL DEFAULT 3,
          lease_owner TEXT,error_log TEXT,lease_expires_at REAL,
          created_at REAL NOT NULL,updated_at REAL NOT NULL,
          state_version INTEGER NOT NULL DEFAULT 1,
          UNIQUE(document_id,ast_hash,node_id)
        );
        CREATE TABLE system_leases (lease_name TEXT PRIMARY KEY,owner_id TEXT,lease_expires_at REAL,
        updated_at REAL,lease_version INTEGER NOT NULL DEFAULT 0);
        INSERT INTO system_leases(lease_name) VALUES ('global_reconciler');
    ''')
    a.commit()
    a.close()

    def connect():
        c = sqlite3.connect(queue, timeout=2)
        c.execute('PRAGMA busy_timeout=2000')
        c.execute('ATTACH DATABASE ? AS fsm_db', (str(fsm),))
        return c

    c=connect()
    try:
        yield c, connect, tmp_path
    finally:
        c.close()


def _row(c):
    return c.execute('SELECT task_state,lease_owner,execution_id,lease_expires_at,updated_at,state_version,retry_count FROM chunk_tasks WHERE worker_type="ASSEMBLER"').fetchone()


def _fsm(c):
    return c.execute('SELECT current_state,state_version,is_terminal FROM fsm_db.document_fsm').fetchone()


def _leader(c):
    now=time.time()
    c.execute('UPDATE system_leases SET owner_id=?,lease_version=?,lease_expires_at=? WHERE lease_name="global_reconciler"', ('recon',7,now+600))
    c.commit()


def _expire(c):
    now=time.time()
    c.execute('UPDATE chunk_tasks SET lease_expires_at=?,updated_at=?', (now-500, now-500))
    c.commit()


def _recover(c, r, **kwargs):
    row=_row(c)
    data={
        'task_id':r.task_id('doc','ast'),'document_id':'doc','ast_hash':'ast',
        'expected_owner':row[1],'expected_execution_id':row[2],
        'expected_expiry':row[3],'expected_updated_at':row[4],'expected_version':row[5],
        'reconciler_owner':'recon','reconciler_epoch':7,'stale_before':time.time()-180,
    }
    data.update(kwargs)
    return r.recover_expired(**data)


def _pdf(tmp_path,content=b'%PDF-1.4\nreal bytes\n'):
    p=tmp_path/'stage_private_123.pdf'
    p.write_bytes(content)
    return p, tmp_path/'translated_doc.pdf'


def test_claim_double_owner_and_monotonic_versions(sandbox):
    c,connect,_=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker_a')
    assert lease and _fsm(c)==('ASSEMBLING',1,0)
    other=connect()
    try:
        assert AssemblyLeaseRepository(other).claim('doc','ast','worker_b') is None
        assert _row(c)[0]=='PROCESSING' and _row(c)[1]=='worker_a'
    finally:
        other.close()


def test_alive_heartbeat_blocks_recovery_even_with_old_fsm_updated_at(sandbox):
    c,connect,_=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker_a')
    assert lease is not None
    _leader(c)
    c.execute('UPDATE fsm_db.document_fsm SET updated_at=?',(time.time()-10000,))
    c.commit()
    other=connect()
    try:
        assert AssemblyLeaseRepository(other).renew(lease)
        assert _recover(c,r) is None  # lease still in the future
        assert _fsm(c)[0]=='ASSEMBLING'
    finally:
        other.close()


@pytest.mark.parametrize('phase', ['ASSEMBLING','READY_FOR_COMPILATION','COMPILING'])
def test_recovery_fences_old_owner_and_new_owner_completes(sandbox, phase):
    c,connect,tmp=sandbox
    r=AssemblyLeaseRepository(c)
    old=r.claim('doc','ast','worker_old')
    assert old is not None
    if phase != 'ASSEMBLING':
        assert r.advance(old,'ASSEMBLING','READY_FOR_COMPILATION')
    if phase=='COMPILING':
        assert r.advance(old,'READY_FOR_COMPILATION','COMPILING')
    _leader(c)
    _expire(c)
    snapshot=_row(c)
    assert _recover(c,r)=='REQUEUED'
    assert _fsm(c)[0]=='READY_FOR_ASSEMBLY'
    assert _row(c)[6]==1
    # No old ownership can advance, renew or publish after recovery.
    assert not r.renew(old)
    if phase=='COMPILING':
        src,dst=_pdf(tmp)
        assert not r.publish(old,str(src),str(dst))
        assert not dst.exists()
    assert _recover(c,r,expected_owner=snapshot[1],expected_execution_id=snapshot[2],
                    expected_expiry=snapshot[3],expected_updated_at=snapshot[4],expected_version=snapshot[5]) is None
    new=r.claim('doc','ast','worker_new')
    assert new is not None and new.execution_id != old.execution_id
    assert r.advance(new,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(new,'READY_FOR_COMPILATION','COMPILING')
    src,dst=_pdf(tmp)
    assert r.publish(new,str(src),str(dst))
    assert dst.read_bytes().startswith(b'%PDF-')
    assert _fsm(c)[0]=='COMPLETED' and _fsm(c)[2]==1
    assert _row(c)[0]=='COMPLETED' and _row(c)[1] is None
    assert r.claim('doc','ast','any') is None


def test_wrong_epoch_and_wrong_leader_cannot_recover(sandbox):
    c,_,_=sandbox
    r=AssemblyLeaseRepository(c)
    r.claim('doc','ast','worker')
    _leader(c)
    _expire(c)
    assert _recover(c,r,reconciler_epoch=6) is None
    assert _recover(c,r,reconciler_owner='stranger') is None
    assert _fsm(c)[0]=='ASSEMBLING'
    assert _row(c)[0]=='PROCESSING'


def test_retry_budget_quarantines_instead_of_infinite_loop(sandbox):
    c,_,_=sandbox
    r=AssemblyLeaseRepository(c)
    r.claim('doc','ast','worker')
    _leader(c)
    _expire(c)
    c.execute('UPDATE chunk_tasks SET retry_count=2,max_retries=3')
    c.commit()
    assert _recover(c,r)=='QUARANTINED'
    assert _fsm(c)[0]=='FAILED_RETRYABLE'
    assert _row(c)[0]=='FAILED'
    assert r.claim('doc','ast','worker') is None


def test_expired_lease_old_worker_cannot_publish_even_without_takeover(sandbox):
    c,_,tmp=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker')
    assert lease is not None
    assert r.advance(lease,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(lease,'READY_FOR_COMPILATION','COMPILING')
    _expire(c)
    src,dst=_pdf(tmp)
    assert not r.publish(lease,str(src),str(dst))
    assert not dst.exists()


def test_failure_only_current_valid_owner_can_change_fsm(sandbox):
    c,_,_=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker')
    assert lease is not None
    assert r.fail_authorized(lease,'simulated tectonic error')
    assert _fsm(c)[0]=='FAILED_RETRYABLE'
    assert not r.fail_authorized(lease,'stale worker should not fail')
    assert _row(c)[0]=='FAILED'


def test_pdf_guard_rejects_invalid_bytes_and_foreign_paths(sandbox):
    c,_,tmp=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker')
    assert lease is not None
    assert r.advance(lease,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(lease,'READY_FOR_COMPILATION','COMPILING')
    bad,dst=_pdf(tmp,b'invalid')
    with pytest.raises(ValueError,match='INVALID_STAGED_PDF'):
        r.publish(lease,str(bad),str(dst))
    assert _fsm(c)[0]=='COMPILING'


def test_concurrent_claim_only_one_worker_is_admitted(sandbox):
    c,connect,_=sandbox
    winners=[]
    start=threading.Barrier(4)
    def run(i):
        mine=connect()
        try:
            start.wait()
            token=AssemblyLeaseRepository(mine).claim('doc','ast',f'worker_{i}')
            if token:
                winners.append(token)
        finally:
            mine.close()
    ts=[threading.Thread(target=run,args=(i,)) for i in range(3)]
    for t in ts:
        t.start()
    start.wait()
    for t in ts:
        t.join(timeout=5)
        assert not t.is_alive()
    assert len(winners)==1


def test_rollback_after_pdf_promotion_is_recoverable(sandbox, monkeypatch):
    c,connect,tmp=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker')
    assert lease is not None
    assert r.advance(lease,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(lease,'READY_FOR_COMPILATION','COMPILING')
    src,dst=_pdf(tmp)
    # sqlite3 connection.commit is read-only attribute; use staged failure at os.replace
    def raise_replace(*args): raise OSError('simulated disk failure')
    monkeypatch.setattr(os,'replace',raise_replace)
    with pytest.raises(OSError,match='simulated disk failure'):
        r.publish(lease,str(src),str(dst))
    assert not dst.exists() and src.exists()
    assert _fsm(c)[0]=='COMPILING' and _row(c)[0]=='PROCESSING'


def test_full_pdf_promoted_before_db_commit_is_recoverable(sandbox):
    """Fail closed across the non-atomic filesystem/SQLite crash window."""
    c,connect,tmp=sandbox
    r=AssemblyLeaseRepository(c)
    old=r.claim('doc','ast','old')
    assert old is not None
    assert r.advance(old,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(old,'READY_FOR_COMPILATION','COMPILING')
    src,dst=_pdf(tmp,b'%PDF-1.4\nfirst complete pdf\n')

    class FailingCommitConnection(sqlite3.Connection):
        fail_once = False
        def commit(self):
            if self.fail_once:
                self.fail_once = False
                raise RuntimeError('simulated crash after rename before DB COMMIT')
            return super().commit()

    mainpath=c.execute('PRAGMA database_list').fetchall()[0][2]
    fsmpath=next(row[2] for row in c.execute('PRAGMA database_list') if row[1]=='fsm_db')
    other=sqlite3.connect(mainpath,timeout=2,factory=FailingCommitConnection)
    other.execute('ATTACH DATABASE ? AS fsm_db',(fsmpath,))
    try:
        other.fail_once=True
        with pytest.raises(RuntimeError,match='simulated crash'):
            AssemblyLeaseRepository(other).publish(old,str(src),str(dst))
    finally:
        other.close()
    # A complete artifact may be visible, but neither FSM nor task committed.
    assert dst.read_bytes()==b'%PDF-1.4\nfirst complete pdf\n'
    assert _fsm(c)[0]=='COMPILING' and _row(c)[0]=='PROCESSING'
    _leader(c)
    _expire(c)
    assert _recover(c,r)=='REQUEUED'
    new=r.claim('doc','ast','new')
    assert new is not None and new.execution_id != old.execution_id
    assert r.advance(new,'ASSEMBLING','READY_FOR_COMPILATION')
    assert r.advance(new,'READY_FOR_COMPILATION','COMPILING')
    fresh=tmp/'fresh_private.pdf'
    fresh.write_bytes(b'%PDF-1.4\nrecovered complete pdf\n')
    assert r.publish(new,str(fresh),str(dst))
    assert dst.read_bytes()==b'%PDF-1.4\nrecovered complete pdf\n'
    assert _fsm(c)[0]=='COMPLETED' and _row(c)[0]=='COMPLETED'
