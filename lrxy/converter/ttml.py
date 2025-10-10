import re

from lxml import etree

from lrxy.exceptions import ParseLyricError, UnexpectedTimingError
from .utils import Data, Line, deformat_time, format_time


def parse_wbw_line(line_tag, ns):
    line: Line = {
        'begin': None,
        'end': None,
        'agent': line_tag.get(f'{{{ns["ttm"]}}}agent'),
        'background': line_tag.get(f'{{{ns["ttm"]}}}role') == 'x-bg',
        'content': []
    }
    inline_bg_lines = []
    word_tags = line_tag.getchildren()

    # if not line['agent']:
    #     line['agent'] = lines[-1]['agent']

    for word_tag in word_tags:
        if word_tag.get(f'{{{ns["ttm"]}}}role') == 'x-bg':
            bg_line, _ = parse_wbw_line(word_tag, ns)
            inline_bg_lines.append(bg_line)
        else:
            line['content'].append({
                'begin': deformat_time(word_tag.get('begin')),
                'end': deformat_time(word_tag.get('end')),
                'part': not word_tag.tail or ' ' not in word_tag.tail,
                'text': word_tag.text
            })

    if not line_tag.get('begin') or not line_tag.get('end'):
        if line['background']:
            line['begin'] = line['content'][0]['begin']
            line['end'] = line['content'][-1]['end']
        else:
            raise TypeError

    else:
        line['begin'] = deformat_time(line_tag.get('begin'))
        line['end'] = deformat_time(line_tag.get('end'))

    return line, inline_bg_lines


def parse_line(line_tag, ns) -> Line:
    return {
        'begin': deformat_time(line_tag.get('begin')),
        'end': deformat_time(line_tag.get('end')),
        'agent': line_tag.get(f'{{{ns["ttm"]}}}agent'),
        'background': line_tag.get(f'{{{ns["ttm"]}}}role') == 'x-bg',
        'content': line_tag.text,
    }


def parse(input_data: str):
    ns = {
        'xmlns': 'http://www.w3.org/ns/ttml',
        'itunes': 'http://music.apple.com/lyric-ttml-internal',
        'ttm': 'http://www.w3.org/ns/ttml#metadata',
    }

    content = re.sub(r'&(?!#?[a-zA-Z0-9]+;)', '&amp;', input_data).encode()

    tree = etree.fromstring(content)
    timing = tree.get(f'{{{ns["itunes"]}}}timing')
    ps = tree.xpath("//xmlns:p", namespaces=ns)
    lines = []

    try:
        if timing in ('Word', 'Syllable'):
            for p in ps:
                line, inline_bg_lines = parse_wbw_line(p, ns)
                lines.append(line)
                lines.extend(inline_bg_lines)
        elif timing == "Line":
            for p in ps:
                line = parse_line(p, ns)
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
        else:
            raise ParseLyricError("ttml", f"Timing {timing} is not supported")
    except TypeError:
        raise UnexpectedTimingError(p.sourceline, "ttml")

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
        # 'dur': format_time(
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
            'begin': format_time(line['begin']),
            'end': format_time(line['end']),
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
                    'begin': format_time(word['begin']),
                    'end': format_time(word['end']),
                })
                span.text = word['text']
                if not word['part']:
                    span.tail = " "

    for agent in sorted(agents, key=lambda s: int(s.removeprefix('v'))):
        agent_tag = etree.SubElement(
            metadata,
            f'{{{ns['ttm']}}}agent',
            attrib={f'{{{ns['xml']}}}id': agent},
        )
        agent_type = 'group'
        if agent in ['v1', 'v2']:
            agent_type = 'person'
        agent_tag.set('type', agent_type)

    return etree.tostring(
        tt,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    ).decode()
