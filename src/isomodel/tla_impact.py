"""E3.4: atomowy rzut pełnego stanu z modelu, ze stałą topologią.

Bez wywołań wykonawcy i ograniczania przejść oczekiwaniami wyroczni.
Wspólnym składnikiem jest wyłącznie parser drzewa składniowego.
"""
import re

from .expressions import compile_expression, UnsupportedSemantics
from .tla_projection import ProjectionError

IDS = ('T01', 'T02', 'T04', 'T05', 'T11', 'T12', 'T13', 'P01', 'P02')
ITEM_FIELDS = {'id':'str','type':'str','state':'str','version':'int','rejections':'int',
               'suspect':'bool','depends_on':'set','predecessor':'str'}
QUESTION_FIELDS = {'id':'str','state':'str','blocking':'bool','age':'int','kind':'str',
                   'about':'str','about_version':'any','requested_transition':'str',
                   'resolution':'str','consumed':'bool'}
HELPER = 'jeśli in_scope(e) i release.state in {ready, reviewed}: release.state := in_preparation; jeśli in_scope(e) i release.state = accepted: next_release_required := true, bez zmiany odebranego rekordu'
EVIDENCE = {'DEC z cytatem użytkownika', 'commit lub tag na polecenie użytkownika',
            'wpis w kolumnie Przejrzane decyzji, która wywołała zmianę; decyzja agenta do podważenia'}


# Rozpoznane opisy są kontraktem translatora, a nie tekstem wykonywanym jako kod.
QUESTION_PROSE = {
    'creation': 'P00: general bez powiązania; change wymaga istniejącego about, operacji z change_operations i blocking=true; about_version pobierane z elementu przy zgłoszeniu; age=max(age)+1. T12 tworzy taki sam rekord open. ID nowego pytania dostarcza zdarzenie.',
    'answer': 'P02: change wymaga jawnego approved/rejected; general ma answered. Dowód DEC zachowuje wynik i powiązanie. Jednoznaczność i wynik odpowiedzi są danymi wejściowymi, nie analizą cytatu.',
    'frame': 'P01–P05 nie zmieniają kind/about/about_version/requested_transition/blocking/age; P03 nie tworzy DEC. T05/T07 atomowo ustawiają consumed=true ze zmianą produktu; błąd nie zużywa zgody.',
}
RELEASE_PROSE = {
    'default_target': 'W01–W05 i W07 zmieniają releases[current_release]; accepted jest końcowe dla konkretnego rekordu',
    'new_release_target': 'W06 czyta stary rekord, lecz from/to opisują zmianę bieżącego wydania: to i skutki dotyczą nowego rekordu numer n + 1; stary rekord pozostaje identyczny',
    'frame': 'pola niewymienione w skutkach pozostają bez zmian; T i P zmieniają produkty robocze i pytania, nigdy zapisane migawki. depends_on po inicjalizacji zmienia wyłącznie T14; predecessor zapisuje tylko T00; scope istniejącego rekordu zmienia tylko W07 w in_preparation',
    'scope_copy': 'W06 kopiuje scope poprzedniego wydania, włącznie z elementami wyłączonymi z dostawy; nie zatwierdza nowego zakresu ani zmian produktów',
    'pending_priority': 'gdy next_release_required = true, następnym przejściem jest W06; nie wolno pominąć W06 po cofnięciu flagi suspect',
    'bounds': 'max_releases jest granicą eksploracji, nie warunkiem W06 w procesie; próba utworzenia wydania poza granicą to granica badania, nie zakleszczenie ani dowód zakończenia',
}


def _validate_semantics_prose(model, transition_ids):
    """Odmowa nieznanego opisu także przy nieaktywnej regule; ID mogą się zmieniać."""
    renamed = dict(zip(IDS, transition_ids))
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, IDS)) + r')\b')
    for section, recognized in (('question_semantics', QUESTION_PROSE),
                                ('release_semantics', RELEASE_PROSE)):
        actual = model.get(section)
        expected_keys = set(recognized)
        if section == 'question_semantics':
            expected_keys |= {'change_operations', 'authorized_change'}
        if not isinstance(actual, dict) or set(actual) != expected_keys:
            raise ProjectionError('Nieobsługiwany zestaw pól ' + section)
        for field, prose in recognized.items():
            expected = pattern.sub(lambda match: renamed[match[0]], prose)
            if actual[field] != expected:
                raise ProjectionError('Nieobsługiwana semantyka opisowa ' + section + '.' + field)


def value_literal(value, field=None):
    """Rekordy/funkcje, sekwencje oraz dwa jawnie wskazane pola zbiorowe.

    Literały TLC/SANY 1.7.4 obsługują Latin-1. Tekst spoza tego zakresu
    powoduje odmowę; dowody nie są normalizowane ani przepisywane.
    """
    if value is None: return '"__null__"'
    if type(value) is bool: return 'TRUE' if value else 'FALSE'
    if type(value) is int: return str(value)
    if isinstance(value, str):
        if any(ord(ch) > 255 for ch in value):
            raise ProjectionError('Literał TLC spoza Latin-1; dowody nie są normalizowane')
        escapes = {'\\': '\\\\', '"': '\\"', '\n': '\\n', '\r': '\\r', '\t': '\\t', '\f': '\\f'}
        # Pozostałe znaki sterujące Latin-1 zapisujemy dosłownie: TLA nie ma sekwencji ucieczki \u ani \b.
        return '"' + ''.join(escapes.get(ch, ch) for ch in value) + '"' 
    if isinstance(value, (list, tuple, set)):
        is_set = field in {'depends_on', 'scope'} or isinstance(value, set)
        values = sorted(value) if is_set else value
        left, right = ('{','}') if is_set else ('<<','>>')
        return left + ', '.join(value_literal(v) for v in values) + right
    if isinstance(value, dict):
        if not value: return '[emptyKey \\in {} |-> 0]'
        if all(isinstance(k,str) and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',k) for k in value):
            return '['+', '.join(k+' |-> '+value_literal(v,k) for k,v in sorted(value.items()))+']'
        if not all(type(k) in (int,str) for k in value): raise ProjectionError('Nieobsługiwany klucz funkcji')
        return '('+' @@ '.join('('+value_literal(k)+' :> '+value_literal(v,k)+')' for k,v in value.items())+')'
    raise ProjectionError(f'Nieobsługiwany literał {value!r}')


def _set(values):
    return '{'+', '.join(value_literal(v) for v in values)+'}'


def validate_command(model, command, world=None):
    fields = {'operation','item','question','actor','checks','evidence','unambiguous','resolution'}
    if not isinstance(command,dict) or set(command) != fields: raise ProjectionError('Wymagane dokładnie osiem pól polecenia')
    if type(command['operation']) is not int or command['operation'] not in range(9): raise ProjectionError('operation wymaga int 0..8')
    if not isinstance(command['actor'],str) or command['actor'] not in model['actors']: raise ProjectionError('Nieznany aktor')
    if any(type(command[k]) is not bool for k in ('checks','evidence','unambiguous')): raise ProjectionError('Wejścia wymagają wartości bool')
    if not isinstance(command['resolution'],str) or command['resolution'] not in ('approved','rejected'): raise ProjectionError('Niepoprawne resolution')
    if any(not isinstance(command[k],str) or not command[k].strip() for k in ('item','question')): raise ProjectionError('Niepoprawne ID przedmiotu operacji')
    op = command['operation']
    if (op >= 7) != (command['item'] == 'none'): raise ProjectionError('Operacje pytań wymagają item=none')
    if (op in (3,5,7,8)) == (command['question'] == 'none'): raise ProjectionError('Niepoprawny argument question')
    if world is not None:
        if op < 7 and command['item'] not in world['items']: raise ProjectionError('Nieznany produkt')
        if op in (3,7,8) and command['question'] not in world['questions']: raise ProjectionError('Nieznane pytanie')
        if op == 5 and command['question'] in world['questions']: raise ProjectionError('ID pytania już istnieje')


def _validate_world(model, world):
    if not isinstance(world,dict) or set(world) != {'items','questions','releases','current_release','next_release_required'}:
        raise ProjectionError('Wymagany pełny stan E2')
    if set(world['items']) != set(model['test_instance']['items']): raise ProjectionError('Wymagany pełny katalog')
    for ident, item in world['items'].items():
        if set(item) != set(ITEM_FIELDS) or item['id'] != ident: raise ProjectionError('Niepoprawny schemat produktu')
        if not isinstance(item['depends_on'],list) or len(set(item['depends_on'])) != len(item['depends_on']) or not set(item['depends_on']) <= world['items'].keys(): raise ProjectionError('Niepoprawny graf zależności')
        for key, kind in ITEM_FIELDS.items():
            if kind in ('int','bool','str') and type(item[key]) is not {'int':int,'bool':bool,'str':str}[kind]: raise ProjectionError('Niepoprawny typ pola produktu')
        if item['type'] not in model['item_types'] or item['state'] not in set(model['item_states'])|{'none'}: raise ProjectionError('Nieznany typ lub stan produktu')
    ages = []
    for ident,q in world['questions'].items():
        if set(q) != set(QUESTION_FIELDS) or q['id'] != ident: raise ProjectionError('Niepoprawny schemat pytania')
        for key, kind in QUESTION_FIELDS.items():
            if kind != 'any' and type(q[key]) is not {'int':int,'bool':bool,'str':str}[kind]: raise ProjectionError('Niepoprawne pole pytania')
        if type(q['about_version']) is not int and q['about_version'] != 'none': raise ProjectionError('Niepoprawna wersja pytania')
        if q['state'] not in model['question_states'] or q['kind'] not in model['question_variables']['kind']['values']: raise ProjectionError('Nieznany stan lub rodzaj pytania')
        if q['age'] < 1: raise ProjectionError('Age pytania musi być dodatnie')
        ages.append(q['age'])
    if len(ages) != len(set(ages)): raise ProjectionError('Age pytań musi być unikatowe')
    if type(world['next_release_required']) is not bool or type(world['current_release']) is not int: raise ProjectionError('Niepoprawne sterowanie wydaniem')
    if world['current_release'] not in world['releases']: raise ProjectionError('Brak bieżącego wydania')
    for n,r in world['releases'].items():
        if type(n) is not int or n < 1 or set(r) != set(model['release_variables']) or r['number'] != n: raise ProjectionError('Niepoprawny rekord wydania')
    value_literal(world)


class Compiler:
    def __init__(self, model, seed, ids):
        self.model, self.seed, self.ids = model, seed, ids
        _validate_world(model,seed)
        if len(ids) != 9 or len(set(ids)) != 9: raise ProjectionError('Wymagane dziewięć różnych przejść')
        if set(model['item_variables']) != set(ITEM_FIELDS)-{'id','type'} or set(model['question_variables']) != set(QUESTION_FIELDS)-{'id'}: raise ProjectionError('Zmieniony schemat zmiennych')
        if model.get('helper_effects') != {'invalidate_release(e)': HELPER}: raise ProjectionError('Nieobsługiwana semantyka helper (także nieaktywnego)')
        _validate_semantics_prose(model, ids)
        self.transitions = []
        for index,ident in enumerate(ids):
            kind = 'item' if index < 7 else 'question'
            matches = [t for t in model[kind+'_transitions'] if t['id'] == ident]
            if len(matches) != 1: raise ProjectionError('Brak lub niejednoznaczność przejścia')
            t = matches[0]
            if set(t)-{'id','name','from','to','actor','guard','effects','evidence','description','iso'}: raise ProjectionError('Nieobsługiwane metadane przejścia')
            actors = [t['actor']] if isinstance(t['actor'],str) else t['actor']
            if not actors or any(a not in model['actors'] for a in actors): raise ProjectionError('Nieznany aktor przejścia')
            if not t['from'] or any(s not in set(model[kind+'_states'])|{'none'} for s in t['from']) or t['to'] not in set(model[kind+'_states'])|{'='}: raise ProjectionError('Nieznany stan przejścia')
            if t.get('evidence') is not None and t['evidence'] not in EVIDENCE: raise ProjectionError('Nieobsługiwany dowód')
            self.transitions.append((kind,t))
        # Sprawdzenie cykli niezależne od wcześniejszego znalezienia źródła w domknięciu.
        visited, active = set(), set()
        def check_dag(node):
            if node in active: raise ProjectionError('Cykl w stałej topologii')
            if node in visited: return
            active.add(node)
            for dependency in seed['items'][node]['depends_on']: check_dag(dependency)
            active.remove(node); visited.add(node)
        for node in seed['items']: check_dag(node)
        if any(type(v['requires_approval']) is not bool for v in model['item_types'].values()):
            raise ProjectionError('Metadane zatwierdzenia wymagają bool')
        if any('initial' in model['question_variables'][k] for k in ('age','blocking')):
            raise ProjectionError('Nieobsługiwana inicjalizacja age/blocking pytania')
        self.closure = {}
        for source in seed['items']:
            def reaches(node, visiting):
                if node in visiting: raise ProjectionError('Cykl w stałej topologii')
                return node == source or any(reaches(d,visiting|{node}) for d in seed['items'][node]['depends_on'])
            self.closure[source] = {i for i in seed['items'] if i != source and reaches(i,set())}

    def expression(self, text, world, kind, transition, *, bound=None, new='{}', expected=None):
        try: tree = compile_expression(text,self.model)
        except (ValueError,UnsupportedSemantics) as error: raise ProjectionError(str(error)) from error
        e = f'{world}.items[c.item]'; q = f'{world}.questions[c.question]'
        release = f'{world}.releases[{world}.current_release]'
        def visit(node, bindings):
            op = node[0]
            if op == 'literal': return value_literal(node[1]), 'bool' if type(node[1]) is bool else 'int'
            if op == 'name':
                name=node[1]
                if name in bindings: return bindings[name]
                if name == 'e': return e,'item'
                if name == 'q': return q,'question'
                if name == 'release': return release,'release'
                if name == 'transition': return value_literal({'id':transition}),'transition'
                if name == 'unambiguous_answer': return 'c.unambiguous','bool'
                if name == 'newly_suspect': return new,'items'
                if name in ('all_items','all_questions'):
                    field = name[4:]; return f'{{{world}.{field}[z] : z \\in DOMAIN {world}.{field}}}',field
                if name in ('current_release','next_release_required'): return f'{world}.{name}', 'int' if name=='current_release' else 'bool'
                if name == 'releases': return f'{world}.releases','releases'
                fields=ITEM_FIELDS if kind=='item' else QUESTION_FIELDS
                if name in fields: return (e if kind=='item' else q)+'.'+name,fields[name]
                if name in self.model['parameters']:
                    v=self.model['parameters'][name]
                    if type(v) not in (int,bool): raise ProjectionError('Nieobsługiwany typ parametru')
                    return value_literal(v),'bool' if type(v) is bool else 'int'
                constants = {'none','blocking_first'}|set().union(*(set(self.model[k+'_states']) for k in ('item','question','release')))
                constants |= {x for v in self.model['question_variables'].values() for x in v.get('values',[])}
                constants |= {t['id'] for k in ('item','question','release') for t in self.model[k+'_transitions']}
                if name in constants: return value_literal(name),'str'
                raise ProjectionError('Nieobsługiwana nazwa wyrażenia: '+name)
            if op == 'attr':
                a,typ=visit(node[1],bindings); field=node[2]
                types = {'item':ITEM_FIELDS,'question':QUESTION_FIELDS,'release':{'state':'str','number':'int','scope':'set','snapshot':'any','acceptance':'any'},'type':{'requires_approval':'bool','depends_on':'set'},'transition':{'id':'str'}}
                if typ not in types or field not in types[typ]: raise ProjectionError('Nieobsługiwany atrybut')
                return f'({a}).{field}',types[typ][field]
            if op == 'index':
                a,typ=visit(node[1],bindings); b,bt=visit(node[2],bindings)
                if typ != 'releases' or bt != 'int': raise ProjectionError('Nieobsługiwane indeksowanie')
                return f'{a}[{b}]','release'
            if op == 'set':
                entries=[visit(ch,bindings) for ch in node[1]]
                if any(t != 'str' for _,t in entries): raise ProjectionError('Obsługiwane są wyłącznie zbiory ID/stanów')
                return '{'+', '.join(v for v,_ in entries)+'}','set'
            if op in ('forall','exists'):
                domain,dt=visit(node[2],bindings)
                typ={'items':'item','questions':'question'}.get(dt)
                if typ is None: raise ProjectionError('Nieobsługiwana dziedzina kwantyfikatora')
                var='bound_'+node[1]
                body,bt=visit(node[3],bindings|{node[1]:(var,typ)})
                if bt != 'bool': raise ProjectionError('Treść kwantyfikatora wymaga bool')
                return '('+('\\A' if op=='forall' else '\\E')+f' {var} \\in {domain}: {body})','bool'
            if op == 'call':
                name=node[1]; args=[visit(ch,bindings) for ch in node[2]]; vals=[a for a,_ in args]
                if name == 'authorized_change':
                    auth=self.model['question_semantics']['authorized_change']
                    if 'authorized_change' in auth: raise ProjectionError('Rekurencyjna definicja zgody')
                    return self.expression(auth,world,kind,transition,bound=bindings|{'q':args[0],'e':args[1]},expected='bool'),'bool'
                if name == 'checks_ok' and args[0][1]=='item': return 'c.checks','bool'
                if name == 'type' and args[0][1]=='item': return f'Types[({vals[0]}).type]','type'
                if name in ('deps','dependents') and args[0][1]=='item':
                    ids=f'({vals[0]}).depends_on' if name=='deps' else f'Closure[({vals[0]}).id]'
                    return f'{{{world}.items[z] : z \\in {ids}}}','items'
                if name == 'in_scope' and args[0][1]=='item': return f'(({vals[0]}).id \\in {release}.scope)','bool'
                if name == 'count' and args[0][1]=='str': return f'Cardinality({{z \\in DOMAIN {world}.questions: {world}.questions[z].state = {vals[0]}}})','int'
                if name in ('oldest','newest') and vals[1]=='"blocking_first"': return f'SelectQuestion({world}, {vals[0]}, '+('FALSE' if name=='oldest' else 'TRUE')+')','question'
                if name == 'answer_resolution' and args[0][1]=='question': return f'(IF ({vals[0]}).kind = "general" THEN "answered" ELSE c.resolution)','str'
                if name == 'copy': return args[0]
                if name == 'item' and args[0][1]=='str': return f'Lookup({world}, {vals[0]})','item'
                if name == 'predecessor' and args[0][1]=='item': return f'Lookup({world}, ({vals[0]}).predecessor)','item'
                raise ProjectionError('Nieobsługiwane wywołanie w wyrażeniu: '+name)
            if op == 'not':
                a,t=visit(node[1],bindings)
                if t!='bool': raise ProjectionError('not wymaga bool')
                return f'~({a})','bool'
            if op not in ('and','or','=>','=','<','+','in','not in','union','minus'): raise ProjectionError('Nieobsługiwany węzeł AST')
            a,at=visit(node[1],bindings); b,bt=visit(node[2],bindings)
            required = 'bool' if op in ('and','or','=>') else 'int' if op in ('<','+') else 'set'
            if op=='=':
                if at != bt and 'any' not in (at,bt): raise ProjectionError('Niezgodność typów równości')
            elif op in ('in','not in'):
                if at!='str' or bt!='set': raise ProjectionError('Niezgodność typów przynależności')
            elif at != required or bt != required: raise ProjectionError('Niezgodność typów operandów')
            symbol={'and':'/\\','or':'\\/','in':'\\in','not in':'\\notin','union':'\\cup','minus':'\\'}.get(op,op)
            return f'({a} {symbol} {b})', 'int' if op=='+' else 'set' if op in ('union','minus') else 'bool'
        code, typ = visit(tree,bound or {})
        if expected is not None and typ not in (expected,'any'): raise ProjectionError('Niezgodny typ wyniku wyrażenia')
        return code

    def effect(self, text, world, records, kind, tid, new='{}'):
        expr=lambda source, expected=None: self.expression(source,world,kind,tid,new=new,expected=expected)
        if text == 'invalidate_release(e)' and kind=='item': return f'Invalidate({world}, c.item)',records
        if text == 'record DEC with user quote' and kind=='question':
            q=f'{world}.questions[c.question]'
            fields={'kind':'"decision"','id':'"SIM_DEC"','question':q+'.id','quote':'"SIM_QUOTE"','simulation':'TRUE'}
            fields.update({k:q+'.'+k for k in ('resolution','about','about_version','requested_transition')})
            return world, f'Append({records}, ['+', '.join(k+' |-> '+v for k,v in fields.items())+'])'
        match=re.fullmatch(r'forall d in (dependents|pre_dependents)\(e\): d\.([a-z_]+) := (.+)',text)
        if match and kind=='item':
            field=match[2]
            if field not in ('version','rejections','suspect'): raise ProjectionError('Zmiana stałej topologii lub nieobsługiwany skutek dla zależnych')
            value=expr(match[3],ITEM_FIELDS[field])
            return f'[{world} EXCEPT !.items = [z \\in DOMAIN {world}.items |-> IF z \\in Closure[c.item] THEN [{world}.items[z] EXCEPT !.{field} = {value}] ELSE {world}.items[z]]]', records
        if text.startswith('create question(') and text.endswith(')') and kind=='item':
            fields={}
            for entry in text[len('create question('):-1].split(','):
                match=re.fullmatch(r'\s*([a-z_]+) = (.+)',entry)
                if not match or match[1] in fields or match[1] not in self.model['question_variables']: raise ProjectionError('Niepoprawne tworzenie pytania')
                fields[match[1]]=match[2]
            if not {'kind','about','requested_transition','blocking'} <= fields.keys(): raise ProjectionError('Tworzenie wymaga pełnego powiązania zmiany')
            values={k:expr(v,QUESTION_FIELDS[k] if QUESTION_FIELDS[k]!='any' else None) for k,v in fields.items()}
            about=values['about']; qvars=self.model['question_variables']
            created={k:value_literal(v['initial']) for k,v in qvars.items() if 'initial' in v}
            created.update(id='c.question',state='"open"',age=f'NextAge({world})',kind=values['kind'],about=about,
                           about_version=f'{world}.items[{about}].version',requested_transition=values['requested_transition'],blocking=values['blocking'])
            constraints=[f'{values["kind"]} = "change"',f'{about} \\in DOMAIN {world}.items',f'{world}.items[{about}].state # "none"',f'{values["requested_transition"]} \\in ChangeOperations',values['blocking'],f'c.question \\notin DOMAIN {world}.questions']
            constraints += [f'{v} = {created[k]}' for k,v in values.items() if k not in ('state',)]
            if 'state' in values: constraints.append(values['state']+' = '+value_literal(qvars['state']['initial']))
            record='['+', '.join(k+' |-> '+v for k,v in created.items())+']'
            result=f'[{world} EXCEPT !.questions = ({world}.questions @@ (c.question :> {record}))]'
            return f'IF Assert('+ ' /\\ '.join('('+v+')' for v in constraints)+', "InputError: niespojna inicjalizacja pytania") THEN '+result+' ELSE '+world,records
        match=re.fullmatch(r'([a-z_]+(?:\.[a-z_]+)?)\s*:=\s*(.+)',text)
        if not match: raise ProjectionError('Nieobsługiwany skutek: '+text)
        target,source=match.groups()
        if (target.startswith('q.') and kind in ('item','question')
                and target[2:] in self.model['question_variables'] and target != 'q.state'):
            field=target[2:]; typ=QUESTION_FIELDS.get(field); path='.questions[c.question].'+field
        elif kind=='item' and target in ('version','rejections','suspect'):
            typ=ITEM_FIELDS[target]; path='.items[c.item].'+target
        elif kind=='question' and target in self.model['question_variables'] and target != 'state':
            typ=QUESTION_FIELDS[target]; path='.questions[c.question].'+target
        elif kind=='observer' and target=='release.state': typ='str'; path=f'.releases[{world}.current_release].state'
        elif kind=='observer' and target=='next_release_required': typ='bool'; path='.next_release_required'
        else: raise ProjectionError('Nieobsługiwany lub stały cel skutku: '+target)
        if typ is None or target=='q.state': raise ProjectionError('Niepoprawny cel pytania')
        return f'[{world} EXCEPT !{path} = {expr(source,typ if typ!="any" else None)}]',records

    def action(self,index,kind,t):
        tid=t['id']; subject='w.items[c.item]' if kind=='item' else 'w.questions[c.question]'
        actors=[t['actor']] if isinstance(t['actor'],str) else t['actor']
        guard=self.expression(t['guard'],'w',kind,tid,expected='bool')
        evidence = bool(t.get('evidence')) or 'record DEC with user quote' in t['effects']
        conditions=['~w.next_release_required',f'c.actor \\in {_set(actors)}',f'{subject}.state \\in {_set(t["from"])}',guard]
        if evidence: conditions.append('c.evidence')
        # Publiczne polecenia walidujemy osobno; polecenia grafu mają poprawne ID.
        valid=f'c.item \\in DOMAIN w.items' if kind=='item' else 'c.question \\in DOMAIN w.questions'
        uses_q='authorized_change(' in t['guard'] or any(e.startswith('q.') for e in t['effects'])
        if kind=='item' and uses_q: valid += ' /\\ c.question \\in DOMAIN w.questions'
        if any(e.startswith('create question(') for e in t['effects']): valid += ' /\\ c.question \\notin DOMAIN w.questions'
        definitions=[f'Enabled{index}(w,c) == IF {valid} THEN '+' /\\ '.join('('+c+')' for c in conditions)+' ELSE FALSE']
        path='.items[c.item]' if kind=='item' else '.questions[c.question]'
        initial='w' if t['to']=='=' else f'[w EXCEPT !{path}.state = {value_literal(t["to"])}]'
        lets=['s0 == '+initial,'r0 == <<>>']; step=0
        for effect in t['effects']:
            w,r=self.effect(effect,f's{step}',f'r{step}',kind,tid)
            step+=1; lets += [f's{step} == {w}',f'r{step} == {r}']
        lets += [f'newSuspect == {{s{step}.items[z] : z \\in {{i \\in DOMAIN w.items: s{step}.items[i].suspect /\\ ~w.items[i].suspect}}}}']
        for observer in self.model['post_step_effects']:
            if set(observer)-{'id','guard','effects','description'}: raise ProjectionError('Nieznane metadane obserwatora')
            condition=self.expression(observer['guard'],f's{step}',kind,tid,new='newSuspect',expected='bool')
            origin=step
            for effect in observer['effects']:
                w,r=self.effect(effect,f's{step}',f'r{step}','observer',tid,new='newSuspect')
                step+=1; lets += [f's{step} == IF {condition} THEN {w} ELSE s{origin}',f'r{step} == {r}']
        definitions += [f'Result{index}(w,c) == LET '+'\n    '.join(lets)+f'\n IN [world |-> s{step}, records |-> r{step}]']
        return '\n'.join(definitions)


def prelude(model, seed, transition_ids=IDS):
    compiler=Compiler(model,seed,transition_ids)
    none=dict(id='none',type='none',state='none',version=0,rejections=0,suspect=False,depends_on=[],predecessor='none')
    definitions=['---- MODULE Impact ----','EXTENDS Integers, Sequences, FiniteSets, TLC',
        'Seed == '+value_literal(seed),'Types == '+value_literal({k:{'requires_approval':v['requires_approval'],'depends_on':v['depends_on']} for k,v in model['item_types'].items()}),
        'Closure == '+value_literal(compiler.closure),'ChangeOperations == '+_set(model['question_semantics']['change_operations']),
        'NoneItem == '+value_literal(none),
        'Lookup(w,id) == IF id = "none" THEN NoneItem ELSE w.items[id]',
        'NextAge(w) == IF DOMAIN w.questions = {} THEN 1 ELSE 1 + (CHOOSE n \\in {w.questions[q].age : q \\in DOMAIN w.questions}: \\A q \\in DOMAIN w.questions: w.questions[q].age <= n)',
        'SelectQuestion(w,state,newest) == LET qs == {w.questions[z] : z \\in {i \\in DOMAIN w.questions: w.questions[i].state = state}} IN IF qs = {} THEN "__null__" ELSE CHOOSE q \\in qs: \\A p \\in qs: (q.blocking \\/ ~p.blocking) /\\ ((q.blocking = p.blocking) => (IF newest THEN q.age >= p.age ELSE q.age <= p.age))',
        'Invalidate(w,id) == LET r == w.releases[w.current_release] IN IF id \\notin r.scope THEN w ELSE IF r.state \\in {"ready", "reviewed"} THEN [w EXCEPT !.releases[w.current_release].state = "in_preparation"] ELSE IF r.state = "accepted" THEN [w EXCEPT !.next_release_required = TRUE] ELSE w']
    definitions += [compiler.action(i,*t) for i,t in enumerate(compiler.transitions)]
    definitions += ['RawEnabled(w,c) == CASE '+'\n [] '.join(f'c.operation = {i} -> Enabled{i}(w,c)' for i in range(9))+'\n [] OTHER -> FALSE',
                    'RawResult(w,c) == CASE '+'\n [] '.join(f'c.operation = {i} -> Result{i}(w,c)' for i in range(9))]
    return '\n'.join(definitions)


def render_probes(model, cases, transition_ids=IDS):
    if not isinstance(cases,list) or not cases: raise ProjectionError('Wymagany niepusty zestaw przypadków')
    seed=cases[0]['before']
    for case in cases:
        if set(case) != {'before','command','expected'}: raise ProjectionError('Niepoprawny schemat próby')
        _validate_world(model,case['before']); validate_command(model,case['command'],case['before'])
        if any(case['before']['items'][i][f] != seed['items'][i][f] for i in seed['items'] for f in ('type','depends_on','predecessor')): raise ProjectionError('Próby w zestawie muszą mieć tę samą stałą topologię')
        if case['expected'] is not None:
            if set(case['expected']) != {'world','records'}: raise ProjectionError('Wymagany pełny stan i records')
            _validate_world(model,case['expected']['world'])
    definitions=[prelude(model,seed,transition_ids),
        'Before == '+value_literal([c['before'] for c in cases]), 'Commands == '+value_literal([c['command'] for c in cases]),
        'ExpectedEnabled == '+value_literal([c['expected'] is not None for c in cases]),
        'ExpectedResult == '+value_literal([c['expected'] or {'world':c['before'],'records':[]} for c in cases]),
        'VARIABLES case_id, phase, world, records',
        f'Init == \\E i \\in 1..{len(cases)}: /\\ case_id = i /\\ phase = 0 /\\ world = Before[i] /\\ records = <<>>',
        'Next == /\\ phase = 0 /\\ RawEnabled(world, Commands[case_id])',
        "        /\\ LET result == RawResult(world, Commands[case_id]) IN /\\ world' = result.world /\\ records' = result.records",
        "        /\\ phase' = 1 /\\ UNCHANGED case_id",
        'Availability == (phase = 0) => (RawEnabled(world, Commands[case_id]) = ExpectedEnabled[case_id])',
        'Successor == (phase = 1) => ([world |-> world, records |-> records] = ExpectedResult[case_id])','====','']
    return '\n'.join(definitions),'INIT Init\nNEXT Next\nINVARIANT Availability\nINVARIANT Successor\nCHECK_DEADLOCK FALSE\n'
