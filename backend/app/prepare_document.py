"""Preparación sin HTML ejecutable ni descargas de recursos del Markdown."""

from markdown_it import MarkdownIt

from app.documents import Document

parser = MarkdownIt('commonmark', {'html': False}).enable('table')


def prepare(document: Document) -> dict:
    blocks = []
    notices = []
    if document.format == 'text':
        blocks = [{'kind': 'paragraph', 'text': document.content}]
    else:
        tokens = parser.parse(document.content.replace('\r\n', '\n').lstrip('\ufeff'))
        index = 0
        quote_depth = 0
        while index < len(tokens):
            token = tokens[index]
            if token.type == 'blockquote_open':
                quote_depth += 1
            elif token.type == 'blockquote_close':
                quote_depth -= 1
            elif token.type in ('fence', 'code_block'):
                blocks.append({'kind': 'code', 'language': token.info.strip() or None, 'text': token.content})
                notices.append('Se omite un bloque de código al leer.')
            elif token.type == 'heading_open':
                blocks.append({'kind': 'heading', 'level': int(token.tag[1:]), 'text': inline_text(tokens[index + 1])})
                index += 2
            elif token.type in ('bullet_list_open', 'ordered_list_open'):
                items = []
                depth = 1
                end = index + 1
                while end < len(tokens) and depth:
                    item = tokens[end]
                    if item.type in ('bullet_list_open', 'ordered_list_open'):
                        depth += 1
                    elif item.type in ('bullet_list_close', 'ordered_list_close'):
                        depth -= 1
                    elif item.type == 'inline':
                        items.append(inline_text(item))
                    end += 1
                blocks.append({'kind': 'list', 'ordered': token.type == 'ordered_list_open', 'items': items})
                index = end - 1
            elif token.type == 'table_open':
                rows = []
                row = []
                index += 1
                while index < len(tokens) and tokens[index].type != 'table_close':
                    cell = tokens[index]
                    if cell.type == 'tr_open':
                        row = []
                    elif cell.type == 'inline':
                        row.append(inline_text(cell))
                    elif cell.type == 'tr_close':
                        rows.append(row)
                    index += 1
                blocks.append({'kind': 'table', 'header': rows[0], 'rows': rows[1:]})
            elif token.type == 'inline':
                kind = 'quote' if quote_depth else 'paragraph'
                blocks.append({'kind': kind, 'text': inline_text(token)})
            index += 1
    spoken = []
    for block in blocks:
        if block['kind'] == 'code':
            continue
        if block['kind'] == 'list':
            spoken.extend(block['items'])
        elif block['kind'] == 'table':
            for row in block['rows']:
                spoken.append('; '.join(f'{heading}: {value}' for heading, value in zip(block['header'], row)))
        else:
            spoken.append(block['text'])
    return {'documentId': document.id, 'revision': document.revision, 'blocks': blocks,
            'spokenText': '\n\n'.join(spoken), 'notices': notices}


def inline_text(token) -> str:
    parts = []
    for child in token.children or []:
        if child.type in ('text', 'code_inline', 'image'):
            parts.append(child.content)
        elif child.type in ('softbreak', 'hardbreak'):
            parts.append('\n')
    return ''.join(parts)
