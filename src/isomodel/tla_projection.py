"""Translator jawnego lokalnego wycinka YAML do akcji TLA+.

Trace: E3.1. Nie jest generatorem pełnego procesu; brak wsparcia to odmowa.
"""
import json
import re
from .expressions import compile_expression, UnsupportedSemantics

FIELDS = {'id': 'str', 'type': 'str', 'state': 'str', 'depends_on': 'set',
          'predecessor': 'str', 'version': 'int', 'rejections': 'int', 'suspect': 'bool'}


class ProjectionError(ValueError):
    """Wejście lub semantyka poza zakresem lokalnego translatora."""


def literal(value):
    if type(value) is bool:
        return 'TRUE' if value else 'FALSE'
    if type(value) is int:
        return str(value)
    if isinstance(value, str):
        # Podzbiór bez sekwencji ucieczki JSON nieobsługiwanych przez TLA+.
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*|=', value):
            raise ProjectionError(f'Nieobsługiwany literał tekstowy: {value!r}')
        return json.dumps(value)
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return '{' + ', '.join(literal(v) for v in sorted(set(value))) + '}'
    if isinstance(value, dict):
        return '[' + ', '.join(f'{k} |-> {literal(v)}' for k, v in sorted(value.items())) + ']'
    raise ProjectionError(f'Nieobsługiwany literał: {value!r}')


def _record(record, model):
    if not isinstance(record, dict) or set(record) != set(FIELDS):
        raise ProjectionError('Rzut musi zawierać dokładnie osiem pól rekordu item.')
    for field, kind in FIELDS.items():
        value = record[field]
        valid = {'str': lambda: isinstance(value, str), 'int': lambda: type(value) is int and value >= 0,
                 'bool': lambda: type(value) is bool, 'set': lambda: isinstance(value, list) and all(isinstance(v, str) for v in value) and len(value) == len(set(value))}[kind]()
        if not valid:
            raise ProjectionError(f'Niepoprawny typ pola {field}.')
    if record['state'] not in model['item_states'] and record['state'] != 'none':
        raise ProjectionError('Nieznany stan produktu.')
    if record['type'] not in model['item_types'] or record['id'] not in model['test_instance']['items']:
        raise ProjectionError('Nieznany produkt lub typ.')
    literal(record)


def _expression(text, model, record, context=None):
    try:
        tree = compile_expression(text, model)
    except (UnsupportedSemantics, ValueError) as error:
        raise ProjectionError(str(error)) from error

    def visit(node, bound=None):
        bound = bound or {}
        op = node[0]
        if op == 'literal':
            return literal(node[1]), 'bool' if type(node[1]) is bool else 'int'
        if op == 'name':
            name = node[1]
            if name in bound:
                return bound[name], 'record'
            if context is not None and name == 'e':
                return record, 'record'
            if name in FIELDS:
                return f'{record}.{name}', FIELDS[name]
            if name in model['parameters'] and type(model['parameters'][name]) in (int, bool):
                value = model['parameters'][name]
                return literal(value), 'bool' if type(value) is bool else 'int'
            if name in model['item_states'] or name == 'none':
                return literal(name), 'str'
            raise ProjectionError(f'Nazwa poza lokalnym wycinkiem: {name}')
        if context is not None:
            if op == 'call' and node[2] == (('name', 'e'),):
                if node[1] == 'checks_ok':
                    return 'checks', 'bool'
                if node[1] == 'deps':
                    return f'Deps({record})', 'records'
                if node[1] == 'type':
                    return f'Types[{record}.type]', 'type_record'
            if op == 'attr':
                parent, kind = visit(node[1], bound)
                field = node[2]
                if kind == 'type_record' and field == 'requires_approval':
                    return parent + '.requires_approval', 'bool'
                if kind == 'record' and field in FIELDS:
                    return parent + '.' + field, FIELDS[field]
                raise ProjectionError('Atrybut poza wycinkiem E3.2.')
            if op == 'set':
                entries = [visit(child, bound) for child in node[1]]
                if any(kind != 'str' for _, kind in entries):
                    raise ProjectionError('Wymagany zbiór stanów.')
                return '{' + ', '.join(value for value, _ in entries) + '}', 'set'
            if op in {'in', 'not in'}:
                left, lk = visit(node[1], bound); right, rk = visit(node[2], bound)
                if lk != 'str' or rk != 'set':
                    raise ProjectionError('Niepoprawne typy przynależności.')
                return f'({left} ' + ('\\in' if op == 'in' else '\\notin') + f' {right})', 'bool'
            if op == 'forall' and node[1] == 'd' and node[2] == ('call', 'deps', (('name', 'e'),)):
                body, kind = visit(node[3], bound | {'d': 'dep'})
                if kind != 'bool':
                    raise ProjectionError('Treść forall musi być bool.')
                return f'(\\A dep \\in Deps({record}): {body})', 'bool'
        if op == 'not':
            value, kind = visit(node[1], bound)
            if kind != 'bool':
                raise ProjectionError('not wymaga bool.')
            return f'~({value})', 'bool'
        if op not in {'<', '=', '+', 'and', 'or', '=>'}:
            raise ProjectionError(f'Operator poza lokalnym wycinkiem: {op}')
        left, lk = visit(node[1], bound); right, rk = visit(node[2], bound)
        required = 'int' if op in {'<', '+'} else 'bool'
        if (op == '=' and lk != rk) or (op != '=' and (lk != required or rk != required)):
            raise ProjectionError(f'Nieobsługiwane typy operandów {op}: {lk}/{rk}')
        symbol = {'and': '/\\', 'or': '\\/'} .get(op, op)
        return f'({left} {symbol} {right})', 'int' if op == '+' else 'bool'
    return visit(tree)


def compile_action(model, transition_id, *, context=None, name='LocalAction'):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
        raise ProjectionError('Niepoprawna nazwa operatora TLA+.')
    if set(model['item_variables']) | {'id', 'type'} != set(FIELDS):
        raise ProjectionError('Zmieniony schemat produktu wymaga przeglądu rzutu E3.1.')
    matches = [t for t in model['item_transitions'] if t['id'] == transition_id]
    if len(matches) != 1:
        raise ProjectionError('Wybierz dokładnie jedno przejście elementu.')
    t = matches[0]
    allowed = {'id', 'name', 'from', 'to', 'actor', 'guard', 'effects', 'iso', 'description'}
    if context is not None:
        allowed.add('evidence')
        if t.get('evidence') not in (None, 'DEC z cytatem użytkownika'):
            raise ProjectionError('Nieobsługiwany rodzaj evidence w E3.2.')
    if set(t) - allowed:
        raise ProjectionError('Metadane wykonawcze przejścia poza wycinkiem E3.1.')
    actors = [t['actor']] if isinstance(t['actor'], str) else t['actor']
    if not isinstance(actors, list) or not actors or any(a not in model['actors'] for a in actors):
        raise ProjectionError('Niepoprawni aktorzy.')
    if not isinstance(t['from'], list) or not t['from'] or any(s not in model['item_states'] and s != 'none' for s in t['from']):
        raise ProjectionError('Niepoprawne stany wejściowe.')
    if t['to'] not in model['item_states'] and t['to'] != '=':
        raise ProjectionError('Nieobsługiwany stan docelowy.')
    guard, kind = _expression(t['guard'], model, 'before', context)
    if kind != 'bool':
        raise ProjectionError('Warunek musi mieć typ bool.')
    states = ['s0 == ' + ('before' if t['to'] == '=' else f'[before EXCEPT !.state = {literal(t["to"])}]')]
    if not isinstance(t['effects'], list):
        raise ProjectionError('effects musi być listą.')
    for i, effect in enumerate(t['effects'], 1):
        match = re.fullmatch(r'(version|rejections|suspect)\s*:=\s*(.+)', effect)
        if not match:
            raise ProjectionError(f'Skutek poza lokalnym wycinkiem: {effect}')
        target, expression = match.groups()
        code, kind = _expression(expression, model, f's{i-1}', context)
        if kind != FIELDS[target]:
            raise ProjectionError(f'Niepoprawny typ przypisania do {target}.')
        states.append(f's{i} == [s{i-1} EXCEPT !.{target} = {code}]')
    args = 'before, after, actor' + (', checks, evidence' if context is not None else '')
    evidence_guard = ['    /\\ evidence'] if context is not None and t.get('evidence') else []
    return '\n'.join([f'{name}({args}) ==',
        f'    /\\ actor \\in {literal(actors)}', f'    /\\ before.state \\in {literal(t["from"])}',
        f'    /\\ {guard}', *evidence_guard, '    /\\ after = LET ' + '\n                   '.join(states),
        f'               IN s{len(t["effects"])}'])


def render_probe(model, transition_id, cases):
    action = compile_action(model, transition_id)
    if not isinstance(cases, list) or not cases:
        raise ProjectionError('Wymagany niepusty zestaw przypadków.')
    seen = set()
    for case in cases:
        if set(case) != {'id', 'actor', 'before', 'enabled', 'after'} or case['id'] in seen:
            raise ProjectionError('Niepoprawny lub powtórzony przypadek.')
        seen.add(case['id'])
        if type(case['enabled']) is not bool or case['actor'] not in model['actors']:
            raise ProjectionError('Niepoprawna dostępność lub aktor przypadku.')
        _record(case['before'], model)
        if case['enabled']:
            _record(case['after'], model)
        elif case['after'] is not None:
            raise ProjectionError('Odmowa nie może deklarować następnika.')
    def sequence(values):
        return '<<\n' + ',\n'.join('    ' + literal(v) for v in values) + '\n>>'
    module = '\n'.join(['---- MODULE Projection ----', 'EXTENDS Integers',
        '\\* Lokalny, syntetyczny test relacji; nie pełny model procesu.', action,
        'Seeds == ' + sequence([c['before'] for c in cases]),
        'Actors == ' + sequence([c['actor'] for c in cases]),
        'ExpectedEnabled == ' + sequence([c['enabled'] for c in cases]),
        'ExpectedAfter == ' + sequence([c['after'] if c['enabled'] else c['before'] for c in cases]),
        'VARIABLES case_id, phase, item',
        f'Init == \\E i \\in 1..{len(cases)}: /\\ case_id = i /\\ phase = 0 /\\ item = Seeds[i]',
        'Next == /\\ phase = 0 /\\ LocalAction(item, item\', Actors[case_id])',
        '        /\\ phase\' = 1 /\\ UNCHANGED case_id',
        'Availability == (phase = 0) => ((ENABLED Next) = ExpectedEnabled[case_id])',
        'Successor == (phase = 1) => (item = ExpectedAfter[case_id])', '====', ''])
    config = 'INIT Init\nNEXT Next\nINVARIANT Availability\nINVARIANT Successor\nCHECK_DEADLOCK FALSE\n'
    return module, config
