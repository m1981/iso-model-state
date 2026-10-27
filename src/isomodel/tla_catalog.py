"""E3.3: dwa aktywne produkty w pełnym katalogu, ze stałą topologią."""
import re
from .tla_projection import ProjectionError, compile_action, literal, _record
from .tla_loop import sequence, parse_value

SUBJECTS = ('p1', 'r1')
TRANSITIONS = ('T00', 'T01', 'T02', 'T03', 'T04')


def validate_command(model, command):
    if not isinstance(command, dict) or set(command) != {'operation','item','actor','checks','evidence'}:
        raise ProjectionError('E3.3 wymaga operation/item/actor/checks/evidence; predecessor poza zakresem.')
    if type(command['operation']) is not int or command['operation'] not in range(5):
        raise ProjectionError('operation musi być liczbą całkowitą 0..4.')
    if not isinstance(command['item'], str) or command['item'] not in SUBJECTS:
        raise ProjectionError('Aktywne produkty E3.3 to p1/r1.')
    if not isinstance(command['actor'], str) or command['actor'] not in model['actors']:
        raise ProjectionError('Nieznany aktor.')
    if type(command['checks']) is not bool or type(command['evidence']) is not bool:
        raise ProjectionError('checks/evidence wymagają bool, nie tekstu lub liczby.')


def validate_items(model, items):
    if not isinstance(items, dict) or set(items) != set(model['test_instance']['items']) or not set(SUBJECTS) <= items.keys():
        raise ProjectionError('Wymagany pełny katalog instancji, w tym p1 i r1.')
    for ident, record in items.items():
        _record(record, model)
        if ident != record['id'] or not set(record['depends_on']) <= items.keys():
            raise ProjectionError('Niepoprawna tożsamość lub nieznana krawędź katalogu.')


def graph_acyclic(items):
    # Własna kontrola translatora: DFS, bez wywoływania predykatu wykonawcy E2.
    done, visiting = set(), set()
    def visit(ident):
        if ident in visiting: return False
        if ident in done: return True
        visiting.add(ident)
        if not all(visit(d) for d in items[ident]['depends_on']): return False
        visiting.remove(ident); done.add(ident)
        return True
    return all(visit(i) for i in items)


def commands():
    return [dict(operation=o, item=i, actor=a, checks=c, evidence=e)
            for i in SUBJECTS for o in range(5) for a in ('A','R','U')
            for c in (False,True) for e in (False,True)]


def prelude(model, seed, transitions):
    validate_items(model, seed)
    if len(transitions) != 5 or len(set(transitions)) != 5:
        raise ProjectionError('Wymagane pięć różnych definicji przejść.')
    types = {k: {'requires_approval': v['requires_approval'], 'depends_on': v['depends_on']} for k,v in model['item_types'].items()}
    if any(type(t['requires_approval']) is not bool or not isinstance(t['depends_on'],list) for t in types.values()):
        raise ProjectionError('Niepoprawne metadane typów.')
    none_record = dict(id='none',type='none',state='none',version=0,rejections=0,suspect=False,depends_on=[],predecessor='none')
    return '\n'.join(['---- MODULE Catalog ----','EXTENDS Integers, Sequences',
        'Types == ' + literal(types), 'Seed == ' + literal(seed),
        'Subjects == ' + literal(list(SUBJECTS)), 'NoneRecord == ' + literal(none_record),
        'GraphAcyclic == ' + literal(graph_acyclic(seed)),
        'Lookup(world, id) == IF id = "none" THEN NoneRecord ELSE world[id]',
        'Deps(e, world) == {world[id] : id \\in e.depends_on}',
        'DependencyTypesOK(world,e,ids) == /\\ ids \\subseteq DOMAIN world /\\ {world[id].type : id \\in ids} = Types[e.type].depends_on',
        *(compile_action(model, ident, name=f'Op{i}', catalog=True) for i,ident in enumerate(transitions)),
        'RawAction(before,after,command) == CASE ' + '\n    [] '.join(f'command.operation = {i} -> Op{i}(before,after,command)' for i in range(5)),
        '    [] OTHER -> FALSE'])


def render_catalog(model, seed, oracle_text, *, transitions=TRANSITIONS, depth=16):
    if type(depth) is not int or not 1 <= depth <= 16:
        raise ProjectionError('Głębokość badania E3.3 musi być 1..16.')
    header = prelude(model, seed, transitions)
    body = [header, oracle_text, 'Commands == ' + sequence(commands()), f'MaxDepth == {depth}',
        'VARIABLES items, depth, used, verified, approved, ok',
        'Init == /\\ items = Seed /\\ depth = 0 /\\ used = [i \\in Subjects |-> 0] /\\ verified = {} /\\ approved = {} /\\ ok = TRUE',
        'Next == /\\ depth < MaxDepth', '        /\\ \\E k \\in DOMAIN Commands:',
        '              /\\ RawAction(items, items\', Commands[k]) /\\ depth\' = depth + 1',
        '              /\\ used\' = IF Commands[k].operation = 3 THEN [used EXCEPT ![Commands[k].item] = @ + 1] ELSE used',
        '              /\\ verified\' = verified \\cup (IF Commands[k].operation = 1 /\\ items\'[Commands[k].item].state = "verified" THEN {Commands[k].item} ELSE {})',
        '              /\\ approved\' = approved \\cup (IF Commands[k].operation = 2 /\\ items\'[Commands[k].item].state = "approved" THEN {Commands[k].item} ELSE {})',
        '              /\\ ok\' = ExpectedAction(items, items\', Commands[k])',
        'Availability == (depth < MaxDepth) => (\\A k \\in DOMAIN Commands: (ENABLED RawAction(items, items\', Commands[k])) = ExpectedEnabled(items, Commands[k]))',
        'Successor == ok', 'HistoryBudget == \\A i \\in Subjects: used[i] <= RefBudget',
        'CounterHistory == \\A i \\in Subjects: items[i].rejections = used[i]',
        'VerifiedHistory == \\A i \\in Subjects: (items[i].state \\in {"approved","baselined"}) => i \\in verified',
        'ApprovedHistory == \\A i \\in Subjects: (items[i].state = "baselined" /\\ items[i].type \\in RefApprovalTypes) => i \\in approved',
        'CreatedVersion == \\A i \\in Subjects: (items[i].state # "none") => items[i].version = RefInitialVersion', '====','']
    config = 'INIT Init\nNEXT Next\n' + ''.join('INVARIANT '+n+'\n' for n in ('Successor','Availability','HistoryBudget','CounterHistory','VerifiedHistory','ApprovedHistory','CreatedVersion')) + 'CHECK_DEADLOCK FALSE\n'
    return '\n'.join(body), config


def render_path(model, seed, inputs, expected, *, transitions=TRANSITIONS):
    if not inputs or len(expected) != len(inputs)+1 or expected[0] != seed:
        raise ProjectionError('Świadek wymaga wszystkich wejść i pełnych oczekiwanych katalogów.')
    for c in inputs: validate_command(model,c)
    for state in expected: validate_items(model,state)
    module = '\n'.join([prelude(model,seed,transitions),'Commands == '+sequence(inputs),
        'ExpectedStates == '+sequence(expected), 'VARIABLES items, depth',
        'Init == /\\ items = Seed /\\ depth = 0',
        'Next == /\\ depth < Len(Commands) /\\ RawAction(items,items\',Commands[depth+1]) /\\ depth\' = depth+1',
        'Availability == (depth < Len(Commands)) => ENABLED Next',
        'Successor == items = ExpectedStates[depth+1]','====',''])
    return module, 'INIT Init\nNEXT Next\nINVARIANT Availability\nINVARIANT Successor\nCHECK_DEADLOCK FALSE\n'


def render_refusal(model, state, command):
    validate_command(model, command)
    return '\n'.join([prelude(model,state,TRANSITIONS), 'Command == '+literal(command),
        'VARIABLES items, depth', 'Init == /\\ items = Seed /\\ depth = 0',
        'Next == /\\ UNCHANGED <<items, depth>> /\\ FALSE', 'Refusal == ~ENABLED RawAction(items,items\',Command)', '====','']), 'INIT Init\nNEXT Next\nINVARIANT Refusal\nCHECK_DEADLOCK FALSE\n'


def parse_dump(text):
    chunks = re.split(r'^State \d+:\s*$', text, flags=re.M)
    if chunks[0].strip(): raise ValueError('Nieznany format dump katalogu.')
    records = []
    for chunk in chunks[1:]:
        state = {}
        for field in re.split(r'^/\\ ',chunk,flags=re.M)[1:]:
            name, sep, value = field.partition(' = ')
            if not sep or name in state: raise ValueError('Niepoprawne pole dump.')
            state[name] = parse_value(value.strip())
        if set(state) not in ({'items','depth'}, {'items','depth','used','verified','approved','ok'}):
            raise ValueError('Niekompletny dump katalogu.')
        records.append(state)
    if not records: raise ValueError('Brak stanów dump.')
    return records
