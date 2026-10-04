import json
from brynz.contract import validate_output
def test_schema_example():
    d={"schema_version":"0.3.0","capture":{"capture_id":"x","tier":"lidar","source":"x","metric_status":"not_calibrated"},
       "device":{},"rooms":[],"walls":[],"openings":[],"measurements":[],"property_plan":{"rooms":[],"connectors":[],"adjacency_graph":[]},
       "damage":[],"concealed_damage_flags":[],"scope":[],"confidence":{"status":"not_calibrated"},"validation":{"status":"NOT_EVALUATED","gates":{},"ground_truth_available":False},"provenance":{},"limitations":[]}
    assert validate_output(d)==[]
