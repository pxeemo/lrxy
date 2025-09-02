import json
import re

from lxml import etree

from .utils import Data, Line, Word, deformatTime, formatLrcTime


def parseTtmlWbwLine(lineTag, ns):
    line: Line = {
        'begin': deformatTime(lineTag.get('begin')),
        'end': deformatTime(lineTag.get('end')),
        'agent': lineTag.get(f'{{{ns["ttm"]}}}agent'),
        'background': lineTag.get(f'{{{ns["ttm"]}}}role') == 'x-bg',
        'content': []
    }
    inlineBgLines = []
    wordTags = lineTag.getchildren()

    # if not line['agent']:
    #     line['agent'] = lines[-1]['agent']

    for wordTag in wordTags:
        if wordTag.get(f'{{{ns["ttm"]}}}role') == 'x-bg':
            bgLine, _ = parseTtmlWbwLine(wordTag, ns)
            inlineBgLines.append(bgLine)
        else:
            wordBegin = deformatTime(wordTag.get('begin'))
            if not line['begin'] and wordBegin:
                line['begin'] = wordBegin
            word: Word = {
                'begin': wordBegin,
                'end': deformatTime(wordTag.get('end')),
                'part': not wordTag.tail or ' ' not in wordTag.tail,
                'text': wordTag.text
            }
            line['content'].append(word)

    if not line['end']:
        lastWordEnd = line['content'][-1]['end']
        if lastWordEnd:
            line['end'] = lastWordEnd

    return line, inlineBgLines


def parseTtmlLine(lineTag, ns):
    line: Line = {
        'begin': deformatTime(lineTag.get('begin')),
        'end': deformatTime(lineTag.get('end')),
        'agent': lineTag.get(f'{{{ns["ttm"]}}}agent'),
        'background': lineTag.get(f'{{{ns["ttm"]}}}role') == 'x-bg',
        'content': lineTag.text,
    }
    return line


def parse(input: str):
    ns = {
        'xmlns': 'http://www.w3.org/ns/ttml',
        'itunes': 'http://music.apple.com/lyric-ttml-internal',
        'ttm': 'http://www.w3.org/ns/ttml#metadata',
    }

    content = re.sub(r'&(?!#?[a-zA-Z0-9]+;)', '&amp;', input).encode()

    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring(content)
    timing = tree.get(f'{{{ns["itunes"]}}}timing')
    ps = tree.xpath("//xmlns:p", namespaces=ns)
    lines = []

    if timing == 'Word':
        for p in ps:
            line, inlineBgLines = parseTtmlWbwLine(p, ns)
            lines.append(line)
            lines.extend(inlineBgLines)
    elif timing == "Line":
        for p in ps:
            line = parseTtmlLine(p, ns)
            lines.append(line)
    elif timing == 'None':
        for p in ps:
            line: Line = {
                'begin': None,
                'end': None,
                'agent': None,
                'background': None,
                'content': p.text,
            }
            lines.append(line)

    data: Data = {
        'timing': timing,
        'lyrics': lines,
    }

    return data


def generate(data: Data):
    ns = {
        None: 'http://www.w3.org/ns/ttml',
        'itunes': 'http://music.apple.com/lyric-ttml-internal',
        'ttm': 'http://www.w3.org/ns/ttml#metadata',
        'xml': 'http://www.w3.org/XML/1998/namespace',
    }

    tt = etree.Element('tt', nsmap=ns, attrib={
        f'{{{ns["itunes"]}}}timing': data['timing'],
        f'{{{ns["xml"]}}}lang': 'en',
    })
    head = etree.SubElement(tt, 'head')
    metadata = etree.SubElement(head, 'metadata')
    body = etree.SubElement(tt, 'body', attrib={
        # 'dur': formatLrcTime(
        #     data['lyrics'][-1]['end'] - data['lyrics'][0]['begin'])
    })
    div = etree.SubElement(body, 'div')
    agents = set()

    for line in data['lyrics']:
        if data['timing'] == 'None':
            p = etree.SubElement(div, 'p')
            p.text = line['content']
            continue

        p = etree.SubElement(div, 'p', attrib={
            'begin': formatLrcTime(line['begin']),
            'end': formatLrcTime(line['end']),
        })
        if line['background']:
            p.set(f'{{{ns['ttm']}}}role', 'x-bg')
        if line['agent']:
            p.set(f'{{{ns['ttm']}}}agent', line['agent'])
            agents.add(line['agent'])

        if data['timing'] == 'Line':
            p.text = line['content']
        elif data['timing'] == 'Word':
            for word in line['content']:
                span = etree.SubElement(p, 'span', attrib={
                    'begin': formatLrcTime(word['begin']),
                    'end': formatLrcTime(word['end']),
                })
                span.text = word['text']
                if not word['part']:
                    span.tail = " "

    for agent in sorted(agents, key=lambda s: int(s.removeprefix('v'))):
        agentTag = etree.SubElement(
            metadata,
            f'{{{ns['ttm']}}}agent',
            attrib={f'{{{ns['xml']}}}id': agent},
        )
        agentType = 'group'
        if agent in ['v1', 'v2']:
            agentType = 'person'
        agentTag.set('type', agentType)

    return etree.tostring(
        tt,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    ).decode()
