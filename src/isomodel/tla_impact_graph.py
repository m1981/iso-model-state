"""Uprząż E3.4: pełny stan, historia wersji i jawne terminalne granice."""
import json
import re
from .tla_impact import prelude, value_literal, IDS

SUBJECTS = ('r1', 'd1', 'a1', 'c1')


def command(operation,item='none',question='none',actor=None,checks=True,evidence=True,unambiguous=True,resolution='approved'):
    return dict(operation=operation,item=item,question=question,actor=actor or ('A','U','U','U','A','A','A','A','U')[operation],
                checks=checks,evidence=evidence,unambiguous=unambiguous,resolution=resolution)


def all_commands():
    result=[]
    for actor in ('A','R','U'):
        for item in SUBJECTS:
            for check in (False,True): result.append(command(0,item,actor=actor,checks=check))
            for op in (1,2,4):
                for evidence in (False,True): result.append(command(op,item,actor=actor,evidence=evidence))
            for q in ('q0','q1','q2'): result.append(command(3,item,q,actor))
            for q in ('q1','q2','q3'): result.append(command(5,item,q,actor))
            result.append(command(6,item,actor=actor))
        for q in ('q0','q1','q2'):
            result.append(command(7,question=q,actor=actor))
            for answer in ('approved','rejected'):
                for clear in (False,True):
                    for evidence in (False,True): result.append(command(8,question=q,actor=actor,resolution=answer,unambiguous=clear,evidence=evidence))
    return result


COMMANDS = all_commands()


def in_domain(world,c):
    if c['operation'] in (3,7,8): return c['question'] in world['questions']
    if c['operation']==5:
        return c['question'] not in world['questions'] and (c['question']!='q3' or all(q in world['questions'] for q in ('q1','q2')))
    return True


def boundary(world,bounds):
    if len(world['questions'])>bounds['max_questions']: return 'questions'
    if any(e['version']>bounds['max_version'] for e in world['items'].values()): return 'version'
    if len(world['releases'])>bounds['max_releases']: return 'releases'
    return 'none'


def initial_history(seed):
    # Jawna historia prefiksu, nie odczyt nazwy bieżącego stanu.
    return {'verified':[[i,1] for i in ('p1','r1','r2','d1','a1','a2','c1')],
            'approved':[[i,1] for i in ('p1','r1','r2','a1','a2')]}


def render_graph(model,seed,oracle_text,*,transition_ids=IDS,depth=16,history=None,invariants=None):
    if type(depth) is not int or not 1<=depth<=16:raise ValueError('Głębokość E3.4 wymaga 1..16')
    history=history or initial_history(seed);bounds=model['test_instance']['bounds']
    as_set=lambda values:'{'+','.join(value_literal(v) for v in values)+'}'
    lines=[prelude(model,seed,transition_ids=transition_ids),oracle_text,
           'Commands == '+value_literal(COMMANDS),
           'Subjects == '+as_set(list(SUBJECTS)),f'MaxDepth == {depth}',
           'InDomain(w,c) == CASE c.operation \\in {3,7,8} -> c.question \\in DOMAIN w.questions',
           ' [] c.operation = 5 -> /\\ c.question \\notin DOMAIN w.questions /\\ (c.question # "q3" \\/ {"q1","q2"} \\subseteq DOMAIN w.questions)',
           ' [] OTHER -> TRUE',
           'Boundary(w) == CASE Cardinality(DOMAIN w.questions) > '+str(bounds['max_questions'])+' -> "questions"',
           ' [] (\\E i \\in DOMAIN w.items: w.items[i].version > '+str(bounds['max_version'])+') -> "version"',
           ' [] Cardinality(DOMAIN w.releases) > '+str(bounds['max_releases'])+' -> "releases" [] OTHER -> "none"',
           'VARIABLES world, depth, verified, approved, records, cut, ok, consumed',
           'Init == /\\ world = Seed /\\ depth = 0 /\\ records = <<>> /\\ cut = "none" /\\ ok = TRUE /\\ consumed = TRUE',
           '        /\\ verified = '+as_set(history['verified'])+' /\\ approved = '+as_set(history['approved']),
           'Next == /\\ depth < MaxDepth /\\ cut = "none"',
           '        /\\ \\E k \\in DOMAIN Commands:',
           '             /\\ InDomain(world,Commands[k])',
           '             /\\ RawEnabled(world,Commands[k])',
           '             /\\ LET c == Commands[k] result == RawResult(world,c) IN',
           '                  /\\ world\' = result.world /\\ records\' = result.records /\\ depth\' = depth+1',
           '                  /\\ cut\' = Boundary(result.world)',
           '                  /\\ ok\' = (IF RefEnabled(world,c) THEN result = RefResult(world,c) ELSE FALSE)',
           '                  /\\ consumed\' = (IF c.operation = 3 THEN result.world.questions[c.question].consumed ELSE TRUE)',
           '                  /\\ verified\' = verified \\cup (IF c.operation = 0 /\\ result.world.items[c.item].state = "verified" THEN {<<c.item,result.world.items[c.item].version>>} ELSE {})',
           '                  /\\ approved\' = approved \\cup (IF c.operation = 1 /\\ result.world.items[c.item].state = "approved" THEN {<<c.item,result.world.items[c.item].version>>} ELSE {})',
           'Availability == (depth < MaxDepth /\\ cut = "none") => (\\A k \\in DOMAIN Commands: InDomain(world,Commands[k]) => (RawEnabled(world,Commands[k]) = RefEnabled(world,Commands[k])))',
           'Successor == ok','Consumed == consumed',
           'VerifiedHistory == \\A i \\in Subjects: (world.items[i].state \\in {"approved","baselined"}) => <<i,world.items[i].version>> \\in verified',
           'ApprovedHistory == \\A i \\in Subjects: (world.items[i].state = "baselined" /\\ world.items[i].type \\in {"PLAN","REQ","AT"}) => <<i,world.items[i].version>> \\in approved','====','']
    inv=invariants or ('Successor','Availability','Consumed','VerifiedHistory','ApprovedHistory')
    return '\n'.join(lines),'INIT Init\nNEXT Next\n'+''.join('INVARIANT '+n+'\n' for n in inv)+'CHECK_DEADLOCK FALSE\n'


def render_path(model,seed,commands,expected,expected_records,*,transition_ids=IDS):
    if len(expected)!=len(commands)+1 or len(expected_records)!=len(commands):raise ValueError('Niepełny świadek')
    lines=[prelude(model,seed,transition_ids=transition_ids),
           'Commands == '+value_literal(commands),'Expected == '+value_literal(expected),
           'ExpectedRecords == '+value_literal([[]]+expected_records),'VARIABLES world, records, depth',
           'Init == /\\ world = Seed /\\ records = <<>> /\\ depth = 0',
           'Next == /\\ depth < Len(Commands)',
           '        /\\ RawEnabled(world,Commands[depth+1])',
           '        /\\ LET r == RawResult(world,Commands[depth+1]) IN /\\ world\' = r.world /\\ records\' = r.records /\\ depth\' = depth+1',
           'Availability == (depth < Len(Commands)) => ENABLED Next',
           'Successor == /\\ world = Expected[depth+1] /\\ records = ExpectedRecords[depth+1]','====','']
    return '\n'.join(lines),'INIT Init\nNEXT Next\nINVARIANT Availability\nINVARIANT Successor\nCHECK_DEADLOCK FALSE\n'


def parse_dump(text):
    states=[]
    for chunk in re.split(r'^State \d+:\s*$',text,flags=re.M)[1:]:
        record={}
        for entry in re.split(r'^/\\ ',chunk,flags=re.M)[1:]:
            name,sep,value=entry.partition(' = ')
            if not sep or name in record:raise ValueError('Błędny dump E3.4')
            record[name]=parse_value(value.strip())
        states.append(record)
    if not states:raise ValueError('Pusty dump E3.4')
    return states


def parse_value(text):
    pattern = re.compile(r'\s*(<<|>>|\|->|:>|@@|[\[\]{}(),]|"(?:[^"\\]|\\.)*"|-?[0-9]+|[A-Za-z_][A-Za-z_0-9]*)')
    tokens=[];pos=0
    while pos<len(text):
        match=pattern.match(text,pos)
        if not match:
            if not text[pos:].strip():break
            raise ValueError('Nieznany token dump: '+text[pos:pos+80])
        tokens.append(match.group(1));pos=match.end()
    at=0
    def take(expected=None):
        nonlocal at
        if at>=len(tokens) or (expected is not None and tokens[at]!=expected):raise ValueError('Niepełny dump')
        value=tokens[at];at+=1;return value
    def peek():return tokens[at] if at<len(tokens) else None
    def value():
        t=take()
        if t=='[':
            result={}
            while True:
                k=take();k=json.loads(k) if k.startswith('"') else int(k) if k.isdecimal() else k
                take('|->');result[k]=value()
                delimiter=take()
                if delimiter==']':return result
                if delimiter!=',':raise ValueError('Błędny rekord')
        if t in ('{','<<'):
            end='}' if t=='{' else '>>';result=[]
            if peek()==end:take(end);return result
            while True:
                result.append(value());delimiter=take()
                if delimiter==end:return result
                if delimiter!=',':raise ValueError('Błędna kolekcja')
        if t=='(':
            first=value()
            if peek()==':>':take(':>');result={first:value()}
            else:
                if not isinstance(first,dict):raise ValueError('Błędna funkcja')
                result=first
            while peek()=='@@':
                take('@@');part=value()
                if isinstance(part,dict):result.update(part)
                else:take(':>');result[part]=value()
            take(')');return result
        if t.startswith('"'):return json.loads(t)
        if t in ('TRUE','FALSE'):return t=='TRUE'
        if t.lstrip('-').isdecimal():return int(t)
        raise ValueError('Nieznana wartość dump '+t)
    result=value()
    if at!=len(tokens):raise ValueError('Nadmiarowy dump')
    return result
