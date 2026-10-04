from benchmark.evaluator import evaluate,compare_series
def test_missing_gt_is_not_evaluated():
    r=evaluate({})
    assert r["status"]=="NOT_EVALUATED"
    assert all(v=="NOT_EVALUATED" for v in r["gates"].values())
def test_compare_series():
    r=compare_series([1,2,3],[1.01,1.9,3.2])
    assert r["n"]==3 and abs(r["max_error_m"]-0.2)<1e-9
