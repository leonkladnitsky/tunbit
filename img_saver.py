import base64
import re
from PIL import Image
from os.path import join
from io import BytesIO


def finder(file_path):
    path_chunks = file_path.split('\\')
    comp_name = path_chunks[5]
    full_fname = path_chunks[-1]
    form_name = full_fname.split('.')[0]

    with open(file=file_path, mode='r+w', encoding="utf8") as form_file:
        html_lines = form_file.readlines()
        img_counter = 0
        for idx, l in enumerate(html_lines):
            found = [m.start() for m in re.finditer('data:image/png', l)]
            if found:
                start = found[0]
                l = l[start:]
                end = [m.start() for m in re.finditer('"', l)][0]
                if end > 0:
                    img_counter += 1
                    img = Image.open(BytesIO(base64.b64decode(l[:end].encode('ascii'))))
                    img_path = path_chunks[:-1]
                    img_fn = f"{comp_name}_{form_name}_{img_counter:02d}.png"
                    if 'PIL.PngImagePlugin.PngImageFile' in str(type(img)) \
                            and "<class 'method'>" in str(type(img.save)):
                        img.save(join(img_path, img_fn))
                        html_lines[idx] = html_lines[idx][:start] + img_fn + html_lines[idx][end:]

                        new_html_lines = []
                        for line in html_lines:
                            if line != '\n':
                                new_html_lines.append(line)

                        form_file.writelines(new_html_lines)
