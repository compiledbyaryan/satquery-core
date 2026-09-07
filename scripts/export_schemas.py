import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from satquery.contracts import (
    AssetRecord,
    ClaimRecord,
    ExecutionEvent,
    PlanRecord,
    ToolContext,
    ToolContract,
    ToolResult,
)

destination=root/'schemas'
destination.mkdir(exist_ok=True)
for cls in (AssetRecord,ToolContract,PlanRecord,ExecutionEvent,ClaimRecord,ToolContext,ToolResult):
    (destination/f'{cls.__name__}.json').write_text(
        json.dumps(cls.model_json_schema(),indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('Exported five core records plus tool context/result. Runtime checks remain mandatory.')
