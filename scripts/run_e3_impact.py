#!/usr/bin/env python3
"""E3.4 — badanie wpływu zmian; nie odbiera etapu E3."""
import argparse
from collections import deque, Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from isomodel import load_model
from isomodel.execution import execute_step, replay, fingerprint, StepRejected, ExplorationBoundary
from isomodel.expressions import InputError
from isomodel.tla_impact import IDS,render_probes,validate_command,value_literal
from isomodel.tla_impact_graph import command,COMMANDS,in_domain,boundary,initial_history,render_graph,render_path,parse_dump
from isomodel.tlc import run_tlc,toolchain_info


def load_oracle():
    spec=importlib.util.spec_from_file_location('impact_oracle',ROOT/'tests/fixtures/e3/impact_oracle.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def canonical(x,field=None):
    if x=='__null__':return None
    if isinstance(x,dict):return {str(k):canonical(v,k) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        if field=='questions' and not x:return {}
        if field=='releases':return {str(i+1):canonical(v) for i,v in enumerate(x)}
        result=[canonical(v) for v in x]
        if field in ('depends_on','scope','verified','approved'):result=sorted(result,key=lambda a:json.dumps(a,sort_keys=True))
        return result
    return x


def key(x):return fingerprint(canonical(x))


def executor(model):
    # Osobna instancja tego samego modułu: cache tylko kompilacji AST, nigdy danych świata.
    spec=importlib.util.spec_from_file_location('isomodel._impact_execution',ROOT/'src/isomodel/execution.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original_expression=module.compile_expression;original_effect=module._compile_effect
    expression=lru_cache(None)(lambda text:original_expression(text,model))
    effect=lru_cache(None)(lambda text,kind:original_effect(text,kind,model))
    module.compile_expression=lambda text,m:expression(text)
    module._compile_effect=lambda text,kind,m:effect(text,kind)
    return module


def event_for(c,ids=IDS):
    event=dict(transition=ids[c['operation']],actor=c['actor'])
    if c['operation']<7:event['item']=c['item']
    if c['operation'] in (3,5,7,8):event['question']=c['question']
    if c['evidence']:event['evidence']=dict(simulation=True,decision='SIM_DEC',reference='SIM_REF',quote='SIM_QUOTE')
    inputs={}
    if c['operation']==0:inputs={'checks_ok':{c['item']:c['checks']}}
    if c['operation']==8:inputs=dict(unambiguous_answer=c['unambiguous'],resolution=c['resolution'])
    return event,inputs


def actual(model,world,c,ids=IDS,engine=None):
    validate_command(model,c,world)
    event,inputs=event_for(c,ids);engine=engine or executor(model)
    if getattr(engine,'omit_question',False) and c['operation']==5:event.pop('question',None)
    try:result=engine.execute_step(model,world,event,inputs)
    except engine.StepRejected:return None
    except engine.ExplorationBoundary:
        # Granice nie występują w guard/effects: osobna kopia zwiększa wyłącznie limity eksploracji.
        extended=deepcopy(model)
        extended['test_instance']['bounds']={k:1000000 for k in extended['test_instance']['bounds']}
        result=engine.execute_step(extended,world,event,inputs)
    assert result['before']==world
    return dict(world=result['after'],records=result['records'])


def next_node(before,c,result,reference,bounds):
    world=result['world'];hist={k:deepcopy(before[k]) for k in ('verified','approved')}
    for op,field,state in ((0,'verified','verified'),(1,'approved','approved')):
        if c['operation']==op and world['items'][c['item']]['state']==state:
            pair=[c['item'],world['items'][c['item']]['version']]
            if pair not in hist[field]:hist[field].append(pair)
    return dict(world=world,depth=before['depth']+1,records=result['records'],cut=boundary(world,bounds),
                ok=canonical(result)==canonical(reference),consumed=c['operation']!=3 or world['questions'][c['question']]['consumed'],**hist)


def python_graph(model,seed,ids=IDS,depth=16,history=None):
    oracle=load_oracle();engine=executor(model);history=history or initial_history(seed)
    init=dict(world=deepcopy(seed),depth=0,records=[],cut='none',ok=True,consumed=True,**deepcopy(history))
    reached={key(init):init};pending=deque([init]);world_cache={};edges=0;cuts=Counter();differences=[]
    start=time.monotonic()
    while pending:
        node=pending.popleft()
        if node['cut']!='none':continue
        if node['depth']==depth:cuts['depth']+=1;continue
        world=node['world'];wid=key(world)
        if wid not in world_cache:
            evaluations=[];snapshot=deepcopy(world)
            for c in COMMANDS:
                if not in_domain(world,c):continue
                expected=oracle.step(world,c,transition_ids=ids)
                observed=actual(model,world,c,ids,engine)
                if canonical(expected)!=canonical(observed):
                    if len(differences)<8:differences.append(dict(before=world,command=c,expected=expected,actual=observed))
                if observed is not None:evaluations.append((c,observed,expected))
            assert world==snapshot
            world_cache[wid]=evaluations
        for c,result,reference in world_cache[wid]:
            edges+=1;after=next_node(node,c,result,reference,model['test_instance']['bounds'])
            if after['cut']!='none':cuts[after['cut']]+=1
            ident=key(after)
            if ident not in reached:reached[ident]=after;pending.append(after)
    return dict(state_hashes=sorted(reached),distinct_states=len(reached),worlds=len(world_cache),edges=edges,
                cuts=dict(cuts),differences=differences,elapsed_seconds=time.monotonic()-start)


def run_module(texts,directory,args):
    directory.mkdir(parents=True,exist_ok=True)
    module=directory/'Impact.tla';cfg=directory/'Impact.cfg';module.write_text(texts[0]);cfg.write_text(texts[1])
    return run_tlc(module,cfg,directory/'runs',java=args.java,jar=args.jar,timeout=args.timeout)


def graph_probe(model,seed,directory,args,ids=IDS,history=None,depth=16):
    oracle=load_oracle()
    result=run_module(render_graph(model,seed,oracle.tla_oracle(transition_ids=ids),transition_ids=ids,history=history,depth=depth),directory,args)
    if result['status']!='passed':return dict(tlc=result,matched=False)
    py=python_graph(model,seed,ids,depth,history)
    dump=parse_dump(Path(result['states_file']).read_text())
    same=sorted({key(s) for s in dump})==py['state_hashes'] and len(dump)==result['distinct_states']
    return dict(tlc=result,python=py,matched=same and not py['differences'],same_state_set=same)


def source_manifest():
    paths=[ROOT/'model/process.yaml',ROOT/'docs/E3-04-MAPOWANIE.md',ROOT/'docs/E3-04-WYROCZNIA.md',
           ROOT/'tests/fixtures/e3/impact_oracle.py',ROOT/'tests/fixtures/e3/impact_cases.py',ROOT/'docs/E3-04-CZULOSC.md',ROOT/'tools/tla-toolchain.json',ROOT/'pyproject.toml',ROOT/'uv.lock',Path(__file__).resolve(),
           *sorted((ROOT/'src/isomodel').glob('*.py')),*sorted((ROOT/'tests').glob('*impact*.py'))]
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}



def load_cases():
    sys.path.insert(0,str(ROOT/'tests/fixtures/e3'))
    spec=importlib.util.spec_from_file_location('impact_cases',ROOT/'tests/fixtures/e3/impact_cases.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def observed_probes(model,cases,engine=None):
    engine=engine or executor(model);observed=[]
    for case in cases:
        before=deepcopy(case['before']);frozen=deepcopy(before)
        actual_result=actual(model,before,case['command'],engine=engine)
        observed.append(dict(id=case['id'],matched=canonical(actual_result)==canonical(case['expected']),actual=actual_result))
        if before!=frozen:raise ValueError('Próba zmieniła dane wejściowe')
    return observed


def probes(model,cases,directory,args):
    result=run_module(render_probes(model,[{k:c[k] for k in ('before','command','expected')} for c in cases]),directory,args)
    observed=observed_probes(model,cases)
    matched=result['status']=='passed' and all(p['matched'] for p in observed)
    if result['status']=='passed':
        dump=parse_dump(Path(result['states_file']).read_text())
        for row in dump:
            case=cases[row['case_id']-1]
            expected=case['expected'] if row['phase']==1 else dict(world=case['before'],records=[])
            matched &= canonical(dict(world=row['world'],records=row['records']))==canonical(expected)
    return dict(tlc=result,python=observed,cases=cases,matched=bool(matched))


def patched(texts,seed,special):
    if special not in ('direct','all'):return texts,None
    closure={i:set(seed['items'])-{i} if special=='all' else {j for j,e in seed['items'].items() if i in e['depends_on']} for i in seed['items']}
    original=next(line for line in texts[0].splitlines() if line.startswith('Closure == '))
    replacement='Closure == '+value_literal(closure)
    module=texts[0].replace(original,replacement)
    return (module,texts[1]),dict(kind=special,original_line=original,replacement_line=replacement,
        original_module_sha256=hashlib.sha256(texts[0].encode()).hexdigest(),mutated_module_sha256=hashlib.sha256(module.encode()).hexdigest())


def mutant_engine(model,special):
    engine=executor(model)
    if special=='all':engine._dependents=lambda world,item:[e for i,e in world['items'].items() if i!=item['id']]
    elif special=='direct':engine._dependents=lambda world,item:[e for e in world['items'].values() if item['id'] in e['depends_on']]
    elif special=='noquestion':engine.omit_question=True
    return engine


def mutation_probe(mutant,directory,args):
    model=mutant['model'];case=mutant['case'];special=mutant.get('special')
    texts,patch=patched(render_probes(model,[{k:case[k] for k in ('before','command','expected')}]),case['before'],special)
    detection=run_module(texts,directory/'detect',args)
    wrong=mutant['wrong_expected']
    witness_case=dict(case,expected=wrong)
    texts,witness_patch=patched(render_probes(model,[{k:witness_case[k] for k in ('before','command','expected')}]),case['before'],special)
    witness=run_module(texts,directory/'witness',args)
    before=deepcopy(case['before']);frozen=deepcopy(before)
    result=actual(model,before,case['command'],engine=mutant_engine(model,special))
    wrong_matches=canonical(result)==canonical(wrong)
    checks={}
    if mutant.get('fieldcheckwanted')=='question_version':
        q=case['command']['question'];item=case['command']['item']
        checks['question_version_differs_from_pre']=result['world']['questions'][q]['about_version']!=before['items'][item]['version']
    if mutant.get('fieldcheckwanted')=='decision_binding':
        q=case['command']['question']
        checks['decision_about_differs_from_pre']=result['records'][0]['about']!=before['questions'][q]['about']
    contract_probe=None
    if special=='noquestion':
        event,inputs=event_for(case['command'])
        engine=executor(model)
        try:engine.execute_step(model,before,event,inputs)
        except InputError as error:contract_probe=dict(status='input_error',message=str(error),original_event=event)
        else:raise ValueError('Brak odmowy nieużywanego question po usunięciu create')
    matched=(detection['status']=='invariant_violation' and detection['invariant']==mutant['expected_violation']
             and witness['status']=='passed' and wrong_matches and before==frozen and all(checks.values()))
    if witness['status']=='passed':
        dump=parse_dump(Path(witness['states_file']).read_text())
        after=[row for row in dump if row['phase']==1]
        matched &= len(after)==1 and canonical(dict(world=after[0]['world'],records=after[0]['records']))==canonical(wrong)
    return dict(id=mutant['id'],special=special,model_sha256=fingerprint(model),case=case,wrong_expected=wrong,
                detection=detection,witness=witness,patch=patch,witness_patch=witness_patch,contract_probe=contract_probe,python=result,field_checks=checks,matched=bool(matched))


def path_probe(model,w,directory,args):
    result=run_module(render_path(model,w['expected'][0],w['commands'],w['expected'],w['records']),directory,args)
    state=deepcopy(w['expected'][0]);engine=executor(model);observed=[]
    for c in w['commands']:
        out=actual(model,state,c,engine=engine)
        if out is None:break
        observed.append(out);state=out['world']
    expected=[dict(world=s,records=r) for s,r in zip(w['expected'][1:],w['records'])]
    matched=result['status']=='passed' and canonical(observed)==canonical(expected)
    if result['status']=='passed':
        dump=sorted(parse_dump(Path(result['states_file']).read_text()),key=lambda r:r['depth'])
        matched &= canonical(dump)==canonical([dict(world=s,records=r,depth=i) for i,(s,r) in enumerate(zip(w['expected'],[[]]+w['records']))])
    return dict(tlc=result,python=observed,commands=w['commands'],expected=w['expected'],expected_records=w['records'],matched=bool(matched))


def verify_prefix(model,oracle):
    trace=replay(model,dict(id='E34_PREFIX',simulation=True,inputs=dict(checks_ok={i:True for i in model['test_instance']['items']},tests_ok=True),events=oracle.prefix_events()))
    history=[dict(transition=r['event']['transition'],operation=IDS.index(r['event']['transition']),item=r['event']['item'],version=r['after']['items'][r['event']['item']]['version'])
             for r in trace['steps'] if r['event']['transition'] in IDS[:3]]
    if not (trace['outcome']=='completed' and canonical(trace['final_state'])==canonical(oracle.initial_state()) and history==oracle.prefix_history()
            and [r['records'] for r in trace['steps']]==oracle.prefix_records()):raise ValueError('Prefiks nie odpowiada niezależnemu oczekiwaniu')
    return trace


def controls(model,seed):
    ids=tuple('RENAMED_'+str(i) for i in range(9));mapping=dict(zip(IDS,ids));pattern=re.compile(r'\b('+'|'.join(IDS)+r')\b')
    def rename(v):
        if isinstance(v,str):return pattern.sub(lambda m:mapping[m[0]],v)
        if isinstance(v,list):return [rename(x) for x in v]
        if isinstance(v,dict):return {k:rename(x) for k,x in v.items()}
        return v
    yield 'renamed',rename(model),rename(seed),ids,None
    m=deepcopy(model);w=deepcopy(seed)
    m['test_instance']['items']['a1']['depends_on']=['r2'];w['items']['a1']['depends_on']=['r2']
    yield 'topology',m,w,IDS,None
    w=deepcopy(seed)
    for i in ('p1','r1','r2','d1','a1','a2','c1'):w['items'][i]['version']=2
    w['questions']['q0']['about_version']=2
    history={field:[[i,2] for i,v in pairs] for field,pairs in initial_history(seed).items()}
    yield 'version',model,w,IDS,history


def boundary_cases(oracle):
    version=oracle.initial_state();version['items']['r1']['version']=3;version['questions']['q0']['about_version']=3
    questions=oracle.witness()['expected'][1]
    for n in (1,2):
        questions['questions']['q'+str(n)]=dict(id='q'+str(n),state='resolved',blocking=True,age=n+1,kind='change',about='a1',about_version=1,requested_transition='T05',resolution='rejected',consumed=False)
    return [dict(id='boundary_version',before=version,command=command(3,'r1','q0'),expected=oracle.step(version,command(3,'r1','q0'))),
            dict(id='boundary_questions',before=questions,command=command(5,'a1','q3'),expected=oracle.step(questions,command(5,'a1','q3')))]


def boundary_evidence(model,cases):
    result=[]
    for c in cases:
        world=deepcopy(c['before']);frozen=deepcopy(world);event,inputs=event_for(c['command'])
        try:execute_step(model,world,event,inputs)
        except ExplorationBoundary as error:reason=str(error)
        else:raise ValueError('Brak oczekiwanego limitu oryginalnego E2')
        after=actual(model,world,c['command'])
        assert world==frozen
        result.append(dict(id=c['id'],original_outcome='ExplorationBoundary',reason=reason,before=frozen,unchanged=world==frozen,
                           extended_candidate=after,boundary=boundary(after['world'],model['test_instance']['bounds']),matched=canonical(after)==canonical(c['expected'])))
    return result


def release_prefixes(model,cases,oracle):
    results=[]
    for case in cases:
        if not case['id'].startswith('R') or case['command']['operation']!=3:continue
        expected=case['before'];release=expected['releases'][1]
        m=deepcopy(model);m['test_instance']['release_scope']=deepcopy(release['scope'])
        events=oracle.prefix_events()
        events[-3]['attributes']['about']=case['command']['item']
        events.append(dict(transition='W01',actor='A'))
        if release['state'] in ('reviewed','accepted'):events.append(dict(transition='W02',actor='R'))
        if release['state']=='accepted':events.append(dict(transition='W04',actor='U',evidence=dict(simulation=True,quote='SIM_QUOTE')))
        trace=replay(m,dict(id=case['id'],simulation=True,inputs=dict(checks_ok={i:True for i in m['test_instance']['items']},tests_ok=True),events=events))
        results.append(dict(id=case['id'],model_sha256=fingerprint(m),trace=trace,matched=trace['outcome']=='completed' and canonical(trace['final_state'])==canonical(expected)))
    return results


def grouped_probes(model,cases,directory,args):
    groups={}
    for c in cases:
        static={i:{f:e[f] for f in ('type','depends_on','predecessor')} for i,e in c['before']['items'].items()}
        groups.setdefault(key(static),[]).append(c)
    results=[probes(model,group,directory/str(n),args) for n,group in enumerate(groups.values())]
    return dict(groups=results,case_count=len(cases),matched=all(r['matched'] for r in results))


def pending_refusals(model,cases):
    results=[]
    for case in cases:
        if not case['id'].endswith('_pending'):continue
        event,inputs=event_for(case['command']);before=deepcopy(case['before'])
        try:execute_step(model,before,event,inputs)
        except StepRejected as error:
            results.append(dict(id=case['id'],before=case['before'],reason=error.code,message=str(error),matched=error.code=='pending_release' and before==case['before']))
        else:results.append(dict(id=case['id'],matched=False))
    return results


def monitor_probe(model,seed,oracle,name,directory,args):
    mutant=deepcopy(model);transition=next(t for t in mutant['item_transitions'] if t['id']=='T05')
    commands=[command(3,'r1','q0')]
    if name=='Consumed':transition['effects'].remove('q.consumed := true')
    else:transition['to']='approved'
    if name=='ApprovedHistory':commands.append(command(2,'r1'))
    r=run_module(render_graph(mutant,seed,oracle.tla_oracle(),invariants=(name,)),directory,args)
    trace=[];confirmed=False
    if r['status']=='invariant_violation':
        blocks=re.findall(r'@!@!@STARTMSG 2217:4 @!@!@\s*(.*?)@!@!@ENDMSG 2217 @!@!@',Path(r['log_file']).read_text(),re.S)
        trace=parse_dump('\n'.join('State '+str(i+1)+':\n'+b.partition('\n')[2] for i,b in enumerate(blocks)))
        final=trace[-1];item=final['world']['items']['r1']
        if name=='Consumed':confirmed=item['state']=='draft' and item['version']==2 and not final['world']['questions']['q0']['consumed'] and not final['consumed']
        else:
            field='verified' if name=='VerifiedHistory' else 'approved';state='approved' if name=='VerifiedHistory' else 'baselined'
            confirmed=item['state']==state and item['version']==2 and ['r1',1] in final[field] and ['r1',2] not in final[field]
        w=deepcopy(seed);expected=[dict(world=w,records=[])];engine=executor(mutant)
        for c in commands:
            out=actual(mutant,w,c,engine=engine);expected.append(out);w=out['world']
        confirmed &= canonical([dict(world=s['world'],records=s['records']) for s in trace])==canonical(expected)
    return dict(id=name,tlc=r,commands=commands,counterexample=trace,counterexample_confirmed=bool(confirmed),
                matched=r['status']=='invariant_violation' and r['invariant']==name and bool(confirmed))


def build(args):
    sources=source_manifest();toolchain_info(args.java,args.jar)
    model=load_model(ROOT/'model/process.yaml');oracle=load_oracle();matrix=load_cases();seed=oracle.initial_state()
    prefix=verify_prefix(model,oracle)
    baseline=graph_probe(model,seed,args.output/'baseline',args)
    print('Baza:',baseline['matched'],flush=True)
    checks=[]
    for name,m,w,ids,hist in controls(model,seed):
        result=graph_probe(m,w,args.output/'controls'/name,args,ids,hist);result['id']=name;checks.append(result)
        print('Kontrola',name,result['matched'],flush=True)
    cases=matrix.cases();valid=[c for c in cases if not c.get('input_error')];invalid=[]
    for c in cases:
        if not c.get('input_error'):continue
        world=deepcopy(c['before']);frozen=deepcopy(world)
        try:actual(model,world,c['command'])
        except (InputError,ValueError) as error:invalid.append(dict(id=c['id'],error=type(error).__name__,message=str(error),matched=world==frozen))
        else:invalid.append(dict(id=c['id'],matched=False))
    matrix_result=grouped_probes(model,valid,args.output/'matrix',args)
    prefixes=release_prefixes(model,cases,oracle)
    pending=pending_refusals(model,cases)
    print('Macierz:',matrix_result['matched'],flush=True)
    boundaries=boundary_cases(oracle);boundary_result=probes(model,boundaries,args.output/'boundaries',args)
    boundary_result['original_limit_probes']=boundary_evidence(model,boundaries)
    mutation_results=[]
    for mutant in matrix.mutants(model):
        r=mutation_probe(mutant,args.output/'mutants'/mutant['id'],args);mutation_results.append(r)
        print('Mutant',r['id'],r['matched'],flush=True)
    monitors=[monitor_probe(model,seed,oracle,name,args.output/'monitors'/name,args) for name in ('VerifiedHistory','ApprovedHistory','Consumed')]
    witness=path_probe(model,oracle.witness(),args.output/'witness',args)
    if sources!=source_manifest():raise ValueError('Źródła zmieniły się w trakcie badania; powtórz po zamrożeniu')
    matched=all(r['matched'] for r in [baseline,matrix_result,boundary_result,witness]+checks+invalid+mutation_results+monitors+prefixes+pending+boundary_result['original_limit_probes'])
    return dict(status='checks_passed_not_stage_acceptance' if matched else 'verification_failed',source_files=sources,source_sha256=fingerprint(sources),
                model_sha256=fingerprint(model),prefix=prefix,baseline=baseline,controls=checks,matrix=matrix_result,invalid_inputs=invalid,
                release_prefixes=prefixes,pending_refusals=pending,boundaries=boundary_result,mutants=mutation_results,monitors=monitors,witness=witness)


def tlc_results(value):
    if isinstance(value,dict):
        if 'toolchain' in value and 'status' in value:yield value
        else:
            for v in value.values():yield from tlc_results(v)
    elif isinstance(value,list):
        for v in value:yield from tlc_results(v)


def exit_code(result):
    statuses={r['status'] for r in tlc_results(result)}
    if 'tool_error' in statuses:return 2
    if 'timeout' in statuses:return 3
    return 0 if result['status'] in ('checks_passed_not_stage_acceptance','baseline_only_passed') else 1


def report(result):
    runs=list(tlc_results(result))
    lines=['# E3.4 — wynik badania', '', 'Status: '+result['status']+'. Bez odbioru E3.', '',
           'Przebiegi TLC: '+str(len(runs))+'. Klasyfikacja: '+str(dict(Counter(r['status'] for r in runs)))+'.']
    if 'baseline' in result:
        py=result['baseline'].get('python',{})
        lines+=['',f"Baza: {py.get('distinct_states')} stanów, {py.get('edges')} krawędzi; granice {py.get('cuts')}.",
                f"Macierz: {result['matrix']['case_count']} prób semantycznych + {len(result['invalid_inputs'])} błędy wejścia; mutanty {sum(m['matched'] for m in result['mutants'])}/{len(result['mutants'])}.",
                '', 'Pełne stany, wyjścia, wyniki narzędzi i źródła: evidence.json.']
    return '\n'.join(lines)+'\n'


def main():
    pin=json.loads((ROOT/'tools/tla-toolchain.json').read_text())
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--java',default=pin['java_default']);p.add_argument('--jar',type=Path,default=ROOT/pin['jar_default'])
    p.add_argument('--timeout',type=float,default=60);p.add_argument('--baseline-only',action='store_true',help='Pomiar samej bazy; nie cały DoD')
    args=p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):p.error('Wybierz nowy lub pusty katalog')
    args.output.mkdir(parents=True,exist_ok=True)
    try:
        if args.baseline_only:
            model=load_model(ROOT/'model/process.yaml');oracle=load_oracle()
            result=graph_probe(model,oracle.initial_state(),args.output/'baseline',args)
            result['status']='baseline_only_passed' if result['matched'] else 'verification_failed'
        else:result=build(args)
        (args.output/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (args.output/'report.md').write_text(report(result))
    except (ValueError,OSError) as error:
        print('E3.4: '+str(error),file=sys.stderr);return 2
    print('E3.4:',result['status'],'; bez odbioru E3',flush=True)
    return exit_code(result)


if __name__=='__main__':raise SystemExit(main())
