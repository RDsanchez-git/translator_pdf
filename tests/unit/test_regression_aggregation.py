"""Tests de agregación por corpus (NADR-19 §5.1 R2-R3)."""
from __future__ import annotations

import pytest

from core.benchmark.topology.regression.aggregation import aggregate_corpus_verdicts
from core.benchmark.topology.regression.models import RegressionVerdict


class TestAggregateCorpusVerdicts:
    def test_all_pass_returns_pass(self):
        verdicts = [RegressionVerdict.PASS, RegressionVerdict.PASS]
        assert aggregate_corpus_verdicts(verdicts) == RegressionVerdict.PASS

    def test_one_warning_returns_warning(self):
        verdicts = [RegressionVerdict.PASS, RegressionVerdict.WARNING, RegressionVerdict.PASS]
        assert aggregate_corpus_verdicts(verdicts) == RegressionVerdict.WARNING

    def test_one_hard_fail_returns_hard_fail(self):
        verdicts = [RegressionVerdict.PASS, RegressionVerdict.HARD_FAIL, RegressionVerdict.WARNING]
        assert aggregate_corpus_verdicts(verdicts) == RegressionVerdict.HARD_FAIL

    def test_all_hard_fail_returns_hard_fail(self):
        verdicts = [RegressionVerdict.HARD_FAIL, RegressionVerdict.HARD_FAIL]
        assert aggregate_corpus_verdicts(verdicts) == RegressionVerdict.HARD_FAIL

    def test_empty_verdicts_raises(self):
        with pytest.raises(ValueError, match="Cannot aggregate empty"):
            aggregate_corpus_verdicts([])

    def test_single_verdict(self):
        assert aggregate_corpus_verdicts([RegressionVerdict.WARNING]) == RegressionVerdict.WARNING

    def test_tuple_input(self):
        verdicts = (RegressionVerdict.PASS, RegressionVerdict.WARNING)
        assert aggregate_corpus_verdicts(verdicts) == RegressionVerdict.WARNING