from fasthtml.common import ft_hx


def Svg(*c, viewBox=None, **kwargs):
    return ft_hx("svg", *c, viewBox=viewBox, **kwargs)


def Path(*c, d=None, fill=None, **kwargs):
    return ft_hx("path", *c, d=d, fill=fill, **kwargs)
