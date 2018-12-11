def read_params(name):
    file = open(name, "r")
    lines = file.readlines()

    params = {}

    for line in lines:
        attrs = line[:-1].split(':')
        key = attrs[0]
        value = attrs[1]

        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif value.isdigit():
            value = int(value)

        params[key] = value

    return params
