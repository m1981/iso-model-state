#!/usr/bin/env python3
"""E3.3: odtworzenie grafu dwóch aktywnych produktów, bez odbioru E3."""
import argparse
from collections import deque
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from isomodel import load_model
from isomodel.execution import execute_step, initial_state, StepRejected, fingerprint
from isomodel.tla_catalog import (TRANSITIONS, SUBJECTS, commands, validate_command, validate_items,
                                render_catalog, render_path, render_refusal, parse_dump)
from isomodel.tlc import toolchain_info, run_tlc


def load_oracle():
    spec=importlib.util.spec_from_file_location('catalog_oracle',ROOT/'tests/fixtures/e3/catalog_oracle.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def canonical(value):
    if isinstance(value,dict):
        return {k: sorted(v) if k in ('depends_on','verified','approved') else canonical(v) for k,v in value.items()}
    if isinstance(value,list): return [canonical(v) for v in value]
    return value


def key(state): return fingerprint(canonical(state))


def actual_step(model, items, command, transitions=TRANSITIONS, base=None):
    validate_command(model,command)
    validate_items(model,items)
    state=deepcopy(base) if base is not None else initial_state(model)
    state['items']=deepcopy(items); frozen=deepcopy(state)
    event=dict(transition=transitions[command['operation']],item=command['item'],actor=command['actor'])
    if command['evidence']:
        event['evidence']=dict(simulation=True,decision='DEC-SIM-CATALOG',reference='SIM-COMMIT',quote='Demonstracyjne polecenie w E3.3')
    try:
        result=execute_step(model,state,event,{'checks_ok':{command['item']:command['checks']}})
    except StepRejected:
        assert state==frozen
        return None
    assert state==frozen
    after=deepcopy(result['after']); output=canonical(after['items']); after['items']=deepcopy(items)
    if after!=frozen: raise ValueError('Naruszono globalną ramę E3.3; wymagany przegląd mapowania.')
    return output


def python_graph(model,seed,transitions=TRANSITIONS,budget=2,version=1):
    oracle=load_oracle(); base=initial_state(model)
    init=dict(items=canonical(seed),depth=0,used={i:0 for i in SUBJECTS},verified=[],approved=[],ok=True)
    reached={key(init):init};pending=deque([init]);differences=[];edges=0;difference_count=0
    while pending:
        before=pending.popleft()
        if before['depth']==16: continue
        for c in commands():
            expected=oracle.step(before['items'],c,budget=budget,initial_version=version)
            after=actual_step(model,before['items'],c,transitions,base)
            equal=canonical(expected)==canonical(after)
            if not equal:
                difference_count+=1
                if len(differences)<8: differences.append(dict(before=before,command=c,expected=expected,actual=after))
            if after is None: continue
            edges+=1;used=deepcopy(before['used']);used[c['item']]+=int(c['operation']==3)
            verified=sorted(set(before['verified'])|({c['item']} if c['operation']==1 and after[c['item']]['state']=='verified' else set()))
            approved=sorted(set(before['approved'])|({c['item']} if c['operation']==2 and after[c['item']]['state']=='approved' else set()))
            node=dict(items=after,depth=before['depth']+1,used=used,verified=verified,approved=approved,ok=equal)
            ident=key(node)
            if ident not in reached: reached[ident]=node;pending.append(node)
    return dict(state_hashes=sorted(reached),distinct_states=len(reached),max_depth=max(s['depth'] for s in reached.values()),
                allowed_input_edges=edges,difference_count=difference_count,difference_examples=differences)


def run_module(texts,directory,args):
    directory.mkdir(parents=True,exist_ok=True)
    module,cfg=directory/'Catalog.tla',directory/'Catalog.cfg';module.write_text(texts[0]);cfg.write_text(texts[1])
    return run_tlc(module,cfg,directory/'runs',java=args.java,jar=args.jar,timeout=args.timeout)


def graph_probe(model,seed,directory,args,*,transitions=TRANSITIONS,budget=2,version=1,violation=None):
    oracle=load_oracle(); reference=oracle.tla_oracle(budget,version,graph_acyclic=oracle.acyclic(seed))
    result=run_module(render_catalog(model,seed,reference,transitions=transitions),directory,args)
    py=python_graph(model,seed,transitions,budget,version)
    same=False
    if violation:
        matched=result['status']=='invariant_violation' and result['invariant']==violation and py['difference_count']>0
    else:
        if result['status']=='passed':
            observed=parse_dump(Path(result['states_file']).read_text())
            same=sorted({key(s) for s in observed})==py['state_hashes'] and len(observed)==result['distinct_states']
        matched=result['status']=='passed' and same and py['difference_count']==0
    return dict(model_sha256=fingerprint(model),seed=seed,transitions=transitions,reference_budget=budget,reference_version=version,
                tlc=result,python=py,matched=matched,same_state_set=same)


def path_probe(model,seed,inputs,expected,directory,args):
    result=run_module(render_path(model,seed,inputs,expected),directory,args)
    py=[canonical(seed)]
    for c in inputs:
        after=actual_step(model,py[-1],c)
        if after is None: break
        py.append(after)
    matched=result['status']=='passed' and py==canonical(expected) and result.get('distinct_states')==len(expected)
    if result['status']=='passed':
        observed=sorted(parse_dump(Path(result['states_file']).read_text()),key=lambda s:s['depth'])
        matched &= canonical(observed)==[dict(items=canonical(s),depth=i) for i,s in enumerate(expected)]
    return dict(tlc=result,inputs=inputs,expected=expected,python=py,matched=bool(matched))


def expected_path(seed,updates):
    # Jawne oczekiwane zmiany danych mutantów; bez wywołania jakiegokolwiek wykonawcy.
    states=[deepcopy(seed)]
    for ident,values in updates:
        state=deepcopy(states[-1]);state[ident].update(values);states.append(state)
    return states


def cmd(op,item='p1',actor=None,evidence=None):
    return dict(operation=op,item=item,actor=actor or ('A' if op in (0,1) else 'U'),checks=op==1,evidence=op in (2,4) if evidence is None else evidence)


def bad_seeds(seed):
    types=deepcopy(seed);types['r1']['depends_on']=[]
    cycle=deepcopy(seed);cycle['a1']['depends_on']=['c1']
    return {'dependency_types':types,'acyclic':cycle}


def mutants(model,seed):
    oracle=load_oracle();w=oracle.witness()
    for name in ('create_version','create_actor','dependency_types','acyclic','approval','baseline_dependency','baseline_actor','baseline_evidence'):
        m=deepcopy(model);s=deepcopy(seed);t={t['id']:t for t in m['item_transitions']};violation='Availability'
        inputs=[cmd(0,'r1')];updates=[('r1',dict(state='draft',version=1))]
        if name=='create_version':
            t['T00']['effects']=['predecessor := proposed_predecessor'];updates[0][1]['version']=0;violation='Successor'
        elif name=='create_actor':
            t['T00']['actor']='U';inputs[0]['actor']='U'
        elif name in ('dependency_types','acyclic'):
            s=bad_seeds(seed)[name]
            call='dependency_types_ok(e, e.depends_on)' if name=='dependency_types' else 'acyclic_dependencies(e, e.depends_on)'
            t['T00']['guard']=t['T00']['guard'].replace(call,'true')
        elif name=='approval':
            t['T04']['guard']=t['T04']['guard'].replace('(state = approved or not type(e).requires_approval)','true')
            inputs=[cmd(0),cmd(1),cmd(4)]
            updates=[('p1',dict(state='draft',version=1)),('p1',dict(state='verified')),('p1',dict(state='baselined'))]
        elif name=='baseline_dependency':
            t['T04']['guard']=t['T04']['guard'].replace('forall d in deps(e): d.state = baselined','true')
            inputs=deepcopy(w['inputs'][:6])+[cmd(4,'r1')]
            expected=deepcopy(w['expected'][:7]);last=deepcopy(expected[-1]);last['r1']['state']='baselined';expected.append(last)
        else:
            if name=='baseline_actor': t['T04']['actor']='A'
            else: del t['T04']['evidence']
            inputs=[cmd(0),cmd(1),cmd(2),cmd(4,actor='A' if name=='baseline_actor' else 'U',evidence=name=='baseline_actor')]
            updates=[('p1',dict(state='draft',version=1)),('p1',dict(state='verified')),('p1',dict(state='approved')),('p1',dict(state='baselined'))]
        if name!='baseline_dependency': expected=expected_path(s,updates)
        yield name,m,s,violation,inputs,expected


def source_manifest():
    paths=[ROOT/'model/process.yaml',ROOT/'tools/tla-toolchain.json',ROOT/'pyproject.toml',ROOT/'uv.lock',Path(__file__).resolve(),
           ROOT/'tests/test_tla_catalog.py',ROOT/'tests/fixtures/e3/catalog_oracle.py',ROOT/'docs/E3-03-MAPOWANIE.md',ROOT/'docs/E3-03-WYROCZNIA.md',
           *sorted((ROOT/'src/isomodel').glob('*.py'))]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def build(args):
    sources=source_manifest();info=toolchain_info(args.java,args.jar);out=Path(args.output).resolve()
    if out.exists() and any(out.iterdir()): raise ValueError('Wybierz nowy albo pusty katalog wyniku.')
    out.mkdir(parents=True,exist_ok=True)
    model=load_model(ROOT/'model/process.yaml');seed=canonical(initial_state(model)['items']);oracle=load_oracle()
    if seed!=canonical(oracle.initial_items()): raise ValueError('Niezależna instancja Init nie odpowiada modelowi; potrzebny przegląd.')
    baseline=graph_probe(model,seed,out/'baseline',args)
    controls=[]
    for name in ('renamed','limit','created_version'):
        m=deepcopy(model);ids=TRANSITIONS;budget=2;version=1
        if name=='renamed':
            ids=tuple('RENAMED_'+str(i) for i in range(5))
            for old,new in zip(TRANSITIONS,ids): next(t for t in m['item_transitions'] if t['id']==old)['id']=new
        elif name=='limit': m['parameters']['MAX_REJECTIONS']=budget=1
        else:
            next(t for t in m['item_transitions'] if t['id']=='T00')['effects'][0]='version := 2';version=2
        p=graph_probe(m,seed,out/'controls'/name,args,transitions=ids,budget=budget,version=version);p['id']=name;controls.append(p)
    negative=[]
    for name,s in bad_seeds(seed).items():
        p=graph_probe(model,s,out/'negative_contexts'/name,args);p['id']=name;negative.append(p)
    mutated=[];monitors=[]
    for name,m,s,violation,inputs,expected in mutants(model,seed):
        p=graph_probe(m,s,out/'mutants'/name,args,violation=violation);p.update(id=name,expected_violation=violation)
        p['witness']=path_probe(m,s,inputs,canonical(expected),out/'mutants'/name/'witness',args)
        p['matched'] &= p['witness']['matched'];mutated.append(p)
        if name in ('create_version','approval'):
            monitor='CreatedVersion' if name=='create_version' else 'ApprovedHistory'
            module,cfg=render_catalog(m,s,oracle.tla_oracle())
            cfg='\n'.join(line for line in cfg.splitlines() if not line.startswith('INVARIANT ') or line=='INVARIANT '+monitor)+'\n'
            result=run_module((module,cfg),out/'monitors'/monitor,args)
            monitors.append(dict(id=monitor,tlc=result,matched=result['status']=='invariant_violation' and result['invariant']==monitor))
    w=oracle.witness();expected=canonical(w['expected']);witness=path_probe(model,seed,w['inputs'],expected,out/'witness',args)
    refusals=[]
    for n,refusal in enumerate(w['refusals'],1):
        state=expected[refusal['after_index']];c=refusal['command']
        result=run_module(render_refusal(model,state,c),out/'refusals'/str(n),args)
        refused=actual_step(model,state,c) is None
        refusals.append(dict(after_index=refusal['after_index'],command=c,tlc=result,matched=refused and result['status']=='passed' and result.get('distinct_states')==1))
    if source_manifest()!=sources: raise ValueError('Źródła zmieniły się podczas badania; powtórz po zamrożeniu kodu.')
    good=all(p['matched'] for p in [baseline,witness]+controls+negative+mutated+monitors+refusals)
    return dict(status='checks_passed_not_stage_acceptance' if good else 'verification_failed',scope='T00_T04_two_active_items_fixed_topology_depth16',
                model_sha256=fingerprint(model),source_files=sources,source_sha256=fingerprint(sources),toolchain=info,
                baseline=baseline,controls=controls,negative_contexts=negative,mutants=mutated,monitors=monitors,witness=witness,refusals=refusals)


def render(r):
    lines=['# E3.3 — wykonanie','',f'Wynik: **{r["status"]}**.',f'Hash źródeł: `{r["source_sha256"]}`.','',
           '| Próba | TLC | Stany | Oczekiwanie spełnione |','|---|---|---:|---|']
    for p in [r['baseline']]+r['controls']+r['negative_contexts']+r['mutants']+r['monitors']:
        t=p['tlc'];lines.append(f'| {p.get("id","baseline")} | {t["invariant"] or t["status"]} | {t.get("distinct_states") or "—"} | {p["matched"]} |')
    lines+=['',f'Świadek ośmiu kroków: {r["witness"]["matched"]}; dwie odmowy: {all(p["matched"] for p in r["refusals"])}.',
            'Zakres: pełny katalog, aktywne p1/r1, tylko T00–T04 i predecessor=none, stała topologia, do 16 kroków.',
            'To nie dowód całego procesu, żywotności ani odbiór E3. CHECK_DEADLOCK FALSE dotyczy końca wycinka.','']
    return '\n'.join(lines)


def main():
    pin=json.loads((ROOT/'tools/tla-toolchain.json').read_text())
    parser=argparse.ArgumentParser(description='E3.3: katalog PLAN–REQ. Kody0/1/2/3: OK/rozbieżność/błąd/timeout. Bez odbioru E3.')
    parser.add_argument('--output',default='artifacts/e3-03/run',help='Nowy lub pusty katalog dowodów')
    parser.add_argument('--java',default=pin['java_default'],help='Istniejąca Java; bez instalacji')
    parser.add_argument('--jar',default=str(ROOT/pin['jar_default']),help='Przypięty JAR; bez pobierania')
    parser.add_argument('--timeout',type=float,default=60,help='Limit pojedynczego TLC: 0 < t <=60 s')
    args=parser.parse_args()
    try:
        r=build(args);out=Path(args.output);(out/'evidence.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');(out/'report.md').write_text(render(r))
    except (ValueError,OSError) as error:
        print(f'E3.3: {error}',file=sys.stderr);return 2
    ps=[r['baseline'],r['witness']]+r['controls']+r['negative_contexts']+r['mutants']+r['monitors']+r['refusals']+[p['witness'] for p in r['mutants']]
    statuses={p['tlc']['status'] for p in ps}
    print(f'E3.3: {r["status"]}; raport {out/"report.md"}. Bez odbioru E3.')
    return 2 if 'tool_error' in statuses else 3 if 'timeout' in statuses else 0 if r['status']=='checks_passed_not_stage_acceptance' else 1


if __name__=='__main__': raise SystemExit(main())
