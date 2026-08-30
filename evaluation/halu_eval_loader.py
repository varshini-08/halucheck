from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
@dataclass(frozen=True)
class HaluEvalSample:
    query: str
    response: str
    hallucination: bool
    sample_id: str
def _label(value):
    if isinstance(value,bool): return value
    return str(value).strip().lower() in {'1','true','yes','hallucination','hallucinated','has_hallucination'}
@lru_cache(maxsize=4)
def load_halueval(path):
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(p)
    raw=p.read_text(encoding='utf-8-sig')
    try: data=json.loads(raw)
    except json.JSONDecodeError:
        data=[json.loads(line) for line in raw.splitlines() if line.strip()]
    if isinstance(data,dict): data=data.get('data',data.get('samples',[]))
    if not isinstance(data,list): raise ValueError('HaluEval dataset must be a JSON array or JSONL file')
    result=[]
    for i,row in enumerate(data):
        q=row.get('user_query',row.get('query',row.get('question'))); response=row.get('llm_response',row.get('chatgpt_response',row.get('response',row.get('answer')))); label=row.get('hallucination_label',row.get('hallucination',row.get('label')))
        if not isinstance(q,str) or not isinstance(response,str) or label is None: raise ValueError(f'Sample {i} has missing fields')
        result.append(HaluEvalSample(q,response,_label(label),str(row.get('ID',row.get('id',i)))))
    return tuple(result)
