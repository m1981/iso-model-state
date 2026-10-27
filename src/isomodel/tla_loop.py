"""E3.2: skończona uprząż wielu kroków, z zewnętrzną tabelą wyroczni."""
import json
import re
from .tla_projection import ProjectionError, _record, compile_action, literal


def sequence(values):
    return '<<' + ',\n'.join(sequence(v) if isinstance(v, list) else literal(v) for v in values) + '>>'


def validate_context(model, context):
    if not isinstance(context, dict) or set(context) != {'id', 'item', 'dependencies', 'budget', 'requires_approval'}:
        raise ProjectionError('Niekompletny kontekst E3.2; wymagane item, dependencies, budget, requires_approval i id.')
    if type(context['budget']) is not int or context['budget'] < 0 or type(context['requires_approval']) is not bool:
        raise ProjectionError('budget musi być nieujemnym int, a requires_approval bool.')
    if not isinstance(context['id'], str) or not context['id'] or not isinstance(context['dependencies'], list):
        raise ProjectionError('Wymagane ID kontekstu i lista dependencies.')
    _record(context['item'], model)
    if context['item']['state'] != 'draft' or context['item']['rejections'] != 0:
        raise ProjectionError('E3.2 zaczyna od draft z licznikiem zero.')
    for d in context['dependencies']:
        _record(d, model)
    ids = [d['id'] for d in context['dependencies']]
    if len(ids) != len(set(ids)) or set(ids) != set(context['item']['depends_on']) or context['item']['id'] in ids:
        raise ProjectionError('Kontekst musi zawierać dokładnie bezpośrednie, stałe zależności.')


def validate_command(model, command):
    if not isinstance(command, dict) or set(command) != {'operation', 'actor', 'checks', 'evidence'}:
        raise ProjectionError('Niekompletne polecenie wycinka E3.2.')
    if type(command['operation']) is not int or command['operation'] not in (1, 2, 3):
        raise ProjectionError('operation musi być liczbą 1, 2 albo 3.')
    if not isinstance(command['actor'], str) or command['actor'] not in model['actors']:
        raise ProjectionError('Nieznany aktor polecenia.')
    if type(command['checks']) is not bool or type(command['evidence']) is not bool:
        raise ProjectionError('checks i evidence muszą być bool; tekst false nie jest wartością logiczną.')


def prelude(model, context, transitions):
    validate_context(model, context)
    if len(transitions) != 3 or len(set(transitions)) != 3:
        raise ProjectionError('Wymagane trzy różne przejścia wycinka.')
    deps = context['dependencies']
    types = {k: {'requires_approval': v['requires_approval']} for k, v in model['item_types'].items()}
    if any(type(v['requires_approval']) is not bool for v in types.values()):
        raise ProjectionError('requires_approval musi być bool.')
    dep_value = literal({d['id']: d for d in deps}) if deps else '[id \\in {} |-> 0]'
    return '\n'.join(['---- MODULE Loop ----', 'EXTENDS Integers, Sequences',
        'Dependencies == ' + dep_value, 'Types == ' + literal(types),
        'Deps(e) == {Dependencies[id] : id \\in e.depends_on}',
        *(compile_action(model, ident, context=context, name=f'Op{i}') for i, ident in enumerate(transitions, 1)),
        'RawAction(before, after, command) ==',
        '    CASE command.operation = 1 -> Op1(before, after, command.actor, command.checks, command.evidence)',
        '      [] command.operation = 2 -> Op2(before, after, command.actor, command.checks, command.evidence)',
        '      [] command.operation = 3 -> Op3(before, after, command.actor, command.checks, command.evidence)',
        '      [] OTHER -> FALSE', 'Seed == ' + literal(context['item'])])


def render_loop(model, context, *, states, targets, commands, transitions=('T01', 'T02', 'T03'), depth=8):
    validate_context(model, context)
    if type(depth) is not int or not 1 <= depth <= 8:
        raise ProjectionError('Głębokość E3.2 musi należeć do 1..8.')
    if not states or len(targets) != len(states) or not commands:
        raise ProjectionError('Niekompletna tabela wyroczni.')
    for state in states:
        _record(state, model)
    for command in commands:
        validate_command(model, command)
    if any(len(row) != len(commands) or any(type(i) is not int or not 0 <= i <= len(states) for i in row) for row in targets):
        raise ProjectionError('Niepoprawne indeksy następników wyroczni.')
    header = prelude(model, context, transitions)
    body = [header, 'Commands == ' + sequence(commands), 'ExpectedStates == ' + sequence(states),
            'Targets == ' + sequence(targets), f'MaxDepth == {depth}',
            'Known == {ExpectedStates[i] : i \\in DOMAIN ExpectedStates}',
            'ExpectedIndex(before, k) == IF before \\in Known THEN Targets[CHOOSE i \\in DOMAIN ExpectedStates: ExpectedStates[i] = before][k] ELSE 0',
            'Expected(before, after, k) == LET j == ExpectedIndex(before, k) IN IF j = 0 THEN FALSE ELSE after = ExpectedStates[j]',
            'VARIABLES item, depth, used, seen, ok',
            'Init == /\\ item = Seed /\\ depth = 0 /\\ used = 0 /\\ seen = FALSE /\\ ok = TRUE',
            'Next == /\\ depth < MaxDepth',
            '        /\\ \\E k \\in DOMAIN Commands:',
            '              /\\ RawAction(item, item\', Commands[k])',
            '              /\\ depth\' = depth + 1',
            '              /\\ used\' = used + (IF Commands[k].operation = 3 THEN 1 ELSE 0)',
            '              /\\ seen\' = (seen \\/ item\'.state = "verified")',
            '              /\\ ok\' = Expected(item, item\', k)',
            'Availability == (depth < MaxDepth) => (\\A k \\in DOMAIN Commands: (ENABLED RawAction(item, item\', Commands[k])) = (ExpectedIndex(item, k) # 0))',
            'Successor == ok', f'HistoryBudget == used <= {context["budget"]}',
            'CounterHistory == item.rejections = used',
            'VerifiedHistory == (item.state = "approved") => seen', '====', '']
    config = 'INIT Init\nNEXT Next\nINVARIANT Successor\nINVARIANT Availability\nINVARIANT HistoryBudget\nINVARIANT CounterHistory\nINVARIANT VerifiedHistory\nCHECK_DEADLOCK FALSE\n'
    return '\n'.join(body), config


def render_path(model, context, commands, expected, transitions=('T01', 'T02', 'T03')):
    validate_context(model, context)
    if not commands or len(expected) != len(commands) + 1 or expected[0] != context['item']:
        raise ProjectionError('Świadek wymaga wejścia i oczekiwania dla każdego kroku.')
    for state in expected:
        _record(state, model)
    for command in commands:
        validate_command(model, command)
    module = '\n'.join([prelude(model, context, transitions),
        'Commands == ' + sequence(commands), 'ExpectedStates == ' + sequence(expected),
        'VARIABLES item, depth', 'Init == /\\ item = Seed /\\ depth = 0',
        'Next == /\\ depth < Len(Commands) /\\ RawAction(item, item\', Commands[depth+1]) /\\ depth\' = depth+1',
        'Availability == (depth < Len(Commands)) => ENABLED Next',
        'Successor == item = ExpectedStates[depth+1]', '====', ''])
    return module, 'INIT Init\nNEXT Next\nINVARIANT Availability\nINVARIANT Successor\nCHECK_DEADLOCK FALSE\n'


# Czytamy wyłącznie format dump dla prostych rekordów tego wycinka, bez eval.
TOKEN = re.compile(r'\s*(\|->|[\[\]{},]|"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z_0-9]*|[0-9]+)')


def parse_value(text):
    tokens, pos = [], 0
    while pos < len(text.rstrip()):
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError('Nieobsługiwany zapis w dump TLC.')
        tokens.append(m[1]); pos = m.end()
    at = 0

    def take(want=None):
        nonlocal at
        if at >= len(tokens) or (want is not None and tokens[at] != want):
            raise ValueError('Niekompletny dump TLC.')
        t = tokens[at]; at += 1
        return t

    def value():
        t = take()
        if t == '[':
            result = {}
            while True:
                key = take(); take('|->')
                if key in result:
                    raise ValueError('Powtórzone pole dump.')
                result[key] = value()
                if take() == ']':
                    return result
        if t == '{':
            result = []
            if tokens[at] == '}':
                take('}'); return result
            while True:
                result.append(value())
                if take() == '}':
                    return sorted(result)
        if t.startswith('"'):
            return json.loads(t)
        if t in ('TRUE', 'FALSE'):
            return t == 'TRUE'
        if t.isdecimal():
            return int(t)
        raise ValueError('Nieznana wartość dump TLC.')
    result = value()
    if at != len(tokens):
        raise ValueError('Nadmiarowa treść dump TLC.')
    return result


def parse_dump(text):
    records = []
    chunks = re.split(r'^State \d+:\s*$', text, flags=re.M)
    if chunks[0].strip():
        raise ValueError('Nieznany nagłówek dump TLC.')
    for chunk in chunks[1:]:
        record = {}
        for field in re.split(r'^/\\ ', chunk, flags=re.M)[1:]:
            name, sep, raw = field.partition(' = ')
            if not sep or name in record:
                raise ValueError('Niepoprawne pole dump TLC.')
            record[name] = parse_value(raw.strip())
        if set(record) not in ({'item', 'depth'}, {'item', 'depth', 'used', 'seen', 'ok'}):
            raise ValueError('Niekompletny stan dump TLC.')
        records.append(record)
    if not records:
        raise ValueError('Pusty dump TLC.')
    return records
