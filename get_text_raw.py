import xml.etree.ElementTree as ET
from rapidocr import RapidOCR


# extract all content with tag <a:t></a:t> from the xml file
def extract_text_from_xml(xml_file):
    tree = ET.parse(xml_file)
    text = []
    for node in tree.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
        text.append(node.text)
    return text


def ocr(image):
    engine = RapidOCR()
    result = engine(image)
    return result.txts


def unzip(pptx, output_dir="./pptx"):
    zip_path = pptx.replace(".pptx", ".zip")

    # rename
    import os

    os.rename(pptx, zip_path)

    # extract
    import zipfile

    zipfile.ZipFile(zip_path).extractall(path=output_dir)

    # rename back
    os.rename(zip_path, pptx)


def main(pptx):
    import os

    output_dir = "./pptx"
    unzip(pptx, output_dir)

    slides_txt = {}
    # get all texts from slides
    for xml_doc in os.listdir(os.path.join(output_dir, "ppt/slides")):
        if not xml_doc.endswith(".xml"):
            continue
        slide_id = xml_doc.replace("slide", "").replace(".xml", "")
        slides_txt[f"slide{slide_id}"] = extract_text_from_xml(
            os.path.join(output_dir, "ppt/slides", xml_doc)
        )

    # get all texts from images
    for image in os.listdir(os.path.join(output_dir, "ppt/media")):
        if not image.endswith(".png") and not image.endswith(".jpeg"):
            continue
        img_id = image.replace("image", "").replace(".png", "").replace(".jpeg", "")
        slides_txt[f"img{img_id}"] = ocr(os.path.join(output_dir, "ppt/media", image))

    for k, v in slides_txt.items():
        print(f"Slide {k}:")
        print(v)


if __name__ == "__main__":
    main("hcp01-CBA.pptx")
