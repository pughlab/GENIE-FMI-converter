import re


rr = "{http://integration.foundationmedicine.com/reporting}"
vr = "{http://foundationmedicine.com/compbio/variant-report-external}"
schema = "{http://www.w3.org/2001/XMLSchema}"
instance = "{http://www.w3.org/2001/XMLSchema-instance}"

matches = [(val, re.compile(r"^{}".format(val))) for val in
            (rr, vr, schema, instance)]

class empty_node(object):
    def __init__(self):
        self.text = ""
        self.attrib = {}
        self.tag = ""


# strips the URL suffix
def suffix(matches, inp):
    for m in matches:
        if re.match(m[1], inp):
            return (m[0], re.sub(m[1], "", inp))

    return ("", inp)


class element:
    def __init__(self, matches, node):
        (self.prefix, self.name) = suffix(matches, node.tag)

        self.attrib = node.attrib

        self.text = ""
        if node.text:
            self.text = node.text.strip()

        self.children = []


    def attr(self, inp):
        return self.attrib.get(inp).strip() if self.attrib.get(inp) else None

    
    def find(self, element_name):
        ret = []
        self.find_path(element_name, ret)
        return ret


    def find_path(self, element_name, pre):
        if self.name == element_name:
            pre.append(self)

        elif self.children:
            for child in self.children:
                child.find_path(element_name, pre)


    # returns first element matching full path
    def get(self, item, *items):
        if items and item == self.name:
            return self.get(*items)
            
        for entry in self.children:
            if entry.name == item:
                if items:
                    return entry.get(*items)
                else:
                    return entry
        return element([], empty_node())
    
                
    def __str__(self):
        return self.__to_str__(0)


    def __to_str__(self, depth):
        ret = "\n" + "  " * depth + self.name

        if self.text:
            ret += ": '{}'".format(self.text)

        if self.attrib:
            ret += " {{{} }}".format(
                     ", ".join("{}: '{}' ".format(key[1], val)
                               for key, val in self.attrib.items()))

        if self.children:
            for child in self.children:
                ret += "  " * (depth + 1) + child.__to_str__(depth + 1)

            ret += "\n"

        return ret


def decompose(node):
    ele = element(matches, node)
    ele.children = [decompose(child) for child in node]
    return ele
