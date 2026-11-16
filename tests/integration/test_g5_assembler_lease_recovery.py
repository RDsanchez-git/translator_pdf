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
    published = r.publish(lease,str(src),str(dst))
    assert not dst.exists(), "G5_STALE_LEASE_PUBLISHED_PDF"
    assert published is False, "G5_STALE_LEASE_ACCEPTED"


def test_failure_only_current_valid_owner_can_change_fsm(sandbox):
    c,_,_=sandbox
    r=AssemblyLeaseRepository(c)
    lease=r.claim('doc','ast','worker')
    assert lease is not None
    assert r.fail_authorized(lease,'simulated tectonic error')
    assert _fsm(c)[0]=='FAILED_RETRYABLE'
    assert not r.fail_authorized(lease,'stale worker should not fail')
    assert _row(c)[0]=='FAILED'
