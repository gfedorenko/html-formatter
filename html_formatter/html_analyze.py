def analyze(path):

    # states
    # name
    # name_began
    # name_ended
    # text
    # attr_name
    # attr_value
    # whitespace_expected
    # closing_expected
    # quote_expected

    current_state = {
        'state': '',
        'tag_name': '',
        'tag_type': 'opening',  # opening closing unpaired doctype
        'quote_char': '"',
        'attr_name': '',
        'attr_value': '',
        'doctype_tag': False,
        'level': 0,
        'text': '',
        'new_line': False
    }

    close_check = []
    tags = []
    errors = []
    index = 1

    file = open(path)
    source = file.read()

    for c in source:
        print(current_state['state'], c)
        if c == "\n":
            index += 1

        if current_state['state'] == '':
            if c == '<':
                current_state['text'] = ''
                current_state['state'] = 'name_began'
                current_state['tag_type'] = 'opening'
            else:
                current_state['text'] += c

        elif current_state['state'] == 'name':
            if c.isalpha() or c.isdigit():
                current_state['tag_name'] += c
            elif c == "\n":
                current_state['new_line'] = True
            elif c == '/':
                current_state['state'] = 'closing_expected'

                if current_state['tag_type'] == 'opening':
                    current_state['tag_type'] = 'unpaired'
                    current_state['state'] = 'closing_expected'
                    tags.append({'name': current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'unpaired',
                                 'value': ''})
                else:
                    errors.append({index: 'Invalid tag name'})
            elif c == ' ' or c == "\t":
                current_state['state'] = 'name_ended'
                if current_state['tag_name'] == '!DOCTYPE':
                    tags.append({'name': current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'doctype',
                                 'value': ''})
                if current_state['tag_type'] == 'opening':
                    tags.append({'name': current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'opening',
                                 'value': ''})
                    close_check.append(current_state['tag_name'])
                    current_state['level'] += 1
                elif current_state['tag_type'] == 'closing':
                    if close_check[-1] != current_state['tag_name']:
                        errors.append({index: 'Unmatched closing tag: ' + current_state['tag_name']})
                    close_check.pop()
                    current_state['level'] -= 1
                    tags.append({'name': '/' + current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'closing',
                                 'value': ''})
            elif c == '>':
                current_state['state'] = 'plain'
                if current_state['tag_type'] == 'opening':
                    tags.append({'name': current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'opening',
                                 'value': ''})
                    close_check.append(current_state['tag_name'])
                    current_state['level'] += 1
                elif current_state['tag_type'] == 'closing':
                    if close_check[-1] != current_state['tag_name']:
                        errors.append({index: 'Unmatched closing tag: ' + current_state['tag_name']})
                    close_check.pop()
                    current_state['level'] -= 1
                    tags.append({'name': '/' + current_state['tag_name'],
                                 'level': current_state['level'],
                                 'type': 'closing',
                                 'value': ''})
            else:
                errors.append({index: 'Invalid tag name'})

        elif current_state['state'] == 'name_began':

            current_state['tag_name'] = ''

            if c == ' ' or c == "\t" or c == "\n":
                continue
            elif c == '/':
                if len(close_check) > 0:
                    current_state['tag_type'] = 'closing'
                else:
                    errors.append({index: 'Invalid tag name'})
            elif c.isalpha() or c == '_':
                current_state['state'] = 'name'
                current_state['tag_name'] += c
            elif index == 1 and c == '!':
                current_state['state'] = 'name'
                current_state['tag_name'] += c
                current_state['doctype_tag'] = True
                current_state['tag_type'] = 'unpaired'
            else:
                errors.append({index: 'Invalid tag name'})

        elif current_state['state'] == 'name_ended':
            if c == ' ' or c == "\t" or c == "\n":
                if c == "\n":
                    current_state['new_line'] = True
                continue
            if c == '/':
                current_state['state'] = 'closing_expected'
                if current_state['tag_type'] == 'opening':
                    current_state['tag_type'] = 'unpaired'
                    current_state['state'] = 'closing_expected'
                else:
                    errors.append({index: 'Invalid tag name'})
            elif c == '>':
                current_state['state'] = 'plain'
            elif c.isalpha() or c == '_':
                current_state['state'] = 'attr_name'
                current_state['attr_name'] += c
            elif c == '<':
                current_state['state'] = 'name_began'
                errors.append({index: 'Unclosed tag'})
            else:
                errors.append({index: 'Invalid attribute name'})
        elif current_state['state'] == 'closing_expected':
            if c == '>':
                current_state['state'] = 'plain'
            else:
                errors.append({index: 'Closing tag was expected'})
        elif current_state['state'] == 'plain':
            if c == '<':
                tags.append({'name': current_state['text'],
                             'level': current_state['level'],
                             'type': 'plain',
                             'value': ''})
                current_state['text'] = ''
                current_state['state'] = 'name_began'
                current_state['tag_type'] = 'opening'
            else:
                current_state['text'] += c
        elif current_state['state'] == 'attr_name':
            if c.isalpha() or c.isdigit() or c == '-' or c == '_':
                current_state['attr_name'] += c
            elif c == '=':
                current_state['state'] = 'quote_expected'
            elif c == '>' and current_state['attr_name'] == 'html':
                tags.append({'name': current_state['attr_name'],
                             'level': current_state['level'],
                             'type': 'attr',
                             'value': '',
                             'new_line': current_state['new_line']})
                current_state['state'] = 'plain'
            elif c == '>' and not current_state['doctype_tag']:
                current_state['state'] = 'plain'
                errors.append({index: 'Attribute must be followed by ='})
            else:
                current_state['attr_name'] += c
                errors.append({index: 'Invalid attribute name'})
        elif current_state['state'] == 'quote_expected':
            if c == ' ' or c == "\t" or c == "\n":
                continue
            elif c == '"' or c == "'":
                current_state['quote_char'] = c
                current_state['state'] = 'attr_value'
            else:
                current_state['quote_char'] = None
                current_state['state'] = 'attr_value'
                current_state['attr_value'] += c
                errors.append({index: 'Quote is expected'})
            current_state['attr_value'] = ''
        elif current_state['state'] == 'attr_value':
            if c == current_state['quote_char']:
                current_state['state'] = 'whitespace_expected'
                current_state['attr_value'] = current_state['quote_char'] + current_state['attr_value'] + current_state['quote_char']
                tags.append({'name': current_state['attr_name'],
                             'level': current_state['level'],
                             'type': 'attr',
                             'value': current_state['attr_value'],
                             'new_line': current_state['new_line']})
                current_state['new_line'] = False
                current_state['attr_name'] = ''
                current_state['attr_value'] = ''
            if not current_state['quote_char']:
                if c == '>':
                    current_state['state'] = 'plain'
                elif c == '/':
                    if current_state['tag_type'] == 'opening':
                        current_state['tag_type'] = 'unpaired'
                        current_state['state'] = 'closing_expected'
                    else:
                        errors.append({index: 'Invalid tag'})
                elif c == "\n":
                    current_state['new_line'] = True
                elif c == ' ' or c == "\t":
                    current_state['attr_value'] += c
            else:
                current_state['attr_value'] += c
        elif current_state['state'] == 'whitespace_expected':
            if c == '>':
                current_state['state'] = 'plain'
            elif c == '/':
                if current_state['tag_type'] == 'opening':
                    current_state['tag_type'] = 'unpaired'
                    current_state['state'] = 'closing_expected'
                else:
                    errors.append({index: 'Invalid tag'})
            elif c == ' ' or c == "\t" or c == "\n":
                if c == "\n":
                    tags[-1]['value'] += "\n"
                    current_state['new_line'] = True
                current_state['state'] = 'name_ended'
            else:
                errors.append({index: 'Invalid tag'})

    if current_state['state'] != 'plain':
        errors.append({index: 'HTML is not valid'})
    if len(close_check) > 0:
        errors.append({index: '"' + ','.join(close_check) + '" tags are not closed'})

    i = 0
    attrs = []
    for item in tags[:]:
        if item['type'] == 'attr':
            attrs.append({'name': item['name'],
                          'value': item['value'],
                          'new_line': item['new_line']})
            tags.remove(item)
        else:
            if len(attrs) > 0:
                tags[i-1]['attrs'] = attrs
                attrs = []
            i += 1

    return errors, tags
