"""
Módulo autónomo para generación de códigos de barras (Code 128) en formato SVG.
No requiere dependencias externas ni conexión a internet.
"""

CODE128_PATTERNS = [
    '212222', '222122', '222221', '121223', '121322', '131222', '122213', '122312', '132212', '221213',
    '221312', '231212', '112232', '122132', '122231', '113222', '123122', '123221', '223211', '221132',
    '221231', '213212', '223112', '312131', '311222', '321122', '321221', '312212', '322112', '322211',
    '212123', '212321', '232121', '111323', '131123', '131321', '112313', '132113', '132311', '211313',
    '231113', '231311', '112133', '112331', '132131', '113123', '113321', '133121', '313121', '211331',
    '231131', '213113', '213311', '213131', '311123', '311321', '331121', '312113', '312311', '332111',
    '314111', '221411', '431111', '111224', '111422', '121124', '121421', '141122', '141221', '112214',
    '112412', '122114', '122411', '142112', '142211', '241211', '221114', '413111', '241112', '134111',
    '111242', '121142', '121241', '114212', '124112', '124211', '411212', '421112', '421211', '212141',
    '214121', '412121', '111143', '111341', '131141', '114113', '114311', '411113', '411311', '113141',
    '114131', '311141', '411131', '211412', '211214', '211232', '2331112'
]


def encode_code128(text: str):
    """Codifica texto en módulos (1s y 0s) según estándar Code 128 B."""
    text_clean = str(text).strip()
    if not text_clean:
        text_clean = '000000'

    values = [104]  # Start B
    for char in text_clean:
        val = ord(char) - 32
        values.append(val if 0 <= val <= 95 else 0)

    checksum = values[0]
    for i, val in enumerate(values[1:], 1):
        checksum += i * val
    values.append(checksum % 103)
    values.append(106)  # Stop

    modules = []
    for val in values:
        pattern = CODE128_PATTERNS[val]
        is_bar = True
        for digit in pattern:
            modules.extend(['1' if is_bar else '0'] * int(digit))
            is_bar = not is_bar
    return modules


def generar_codigo_barra_svg(text: str, height: int = 44, module_width: int = 2, show_text: bool = True) -> str:
    """Genera código de barras como SVG válido para incrustar en HTML o imprimir."""
    modules = encode_code128(text)
    total_width = len(modules) * module_width + 16
    svg_height = height + (16 if show_text else 0)

    rects = []
    i = 0
    while i < len(modules):
        if modules[i] == '1':
            start = i
            while i < len(modules) and modules[i] == '1':
                i += 1
            w = (i - start) * module_width
            rx = 8 + start * module_width
            rects.append(f'<rect x="{rx}" y="0" width="{w}" height="{height}" fill="#111" />')
        else:
            i += 1

    text_elem = (
        f'<text x="{total_width / 2}" y="{height + 13}" text-anchor="middle" '
        f'font-family="monospace" font-size="11" font-weight="bold" fill="#111">{text}</text>'
        if show_text else ''
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {svg_height}" '
        f'width="{total_width}" height="{svg_height}" style="display:inline-block; max-width:100%; height:auto;">'
        f'{"".join(rects)}{text_elem}</svg>'
    )
