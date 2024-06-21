import io
import re
from functools import partial
from pathlib import Path
from typing import Protocol, TypedDict, Literal, TypeAlias
from xml.etree import ElementTree

from .elements import ImageElement, TableElement
from .rectangle_utils import is_in_rects, intersects_rects
from .._pymupdf import pymupdf


class Output(TypedDict):
    drawings: list[dict]
    image_elements: list[ImageElement]
    clusters: list[pymupdf.Rect]


class ProcessGraphicsProtocol(Protocol):
    def fit(self, page: pymupdf.Page, table_elements: list[TableElement]) -> Output:
        """Fit page graphics."""


AnnotateImage: TypeAlias = Literal["tesseract", False]
AnnotateImageTuple = ("tesseract", False)


class DefaultGraphicsProcessor(ProcessGraphicsProtocol):
    """Process graphics in PDF files."""

    write_images: Path | None
    annotate_images: AnnotateImage
    dpi: int | None
    minimal_image_size: tuple[int, int]

    def __init__(
        self,
        write_images: Path | None = None,
        annotate_images: AnnotateImage = False,
        dpi: int | None = None,
        minimal_image_size: tuple[int, int] = (30, 30),
    ):
        self.write_images = write_images
        self.annotate_images = annotate_images
        self.dpi = dpi
        self.minimal_image_size = minimal_image_size

        if self.annotate_images not in AnnotateImageTuple:
            raise ValueError(
                f"Invalid Annotator engine '{self.annotate_images}'. Use 'tesseract', or False."
            )

        if self.annotate_images == "tesseract":
            try:
                from PIL import Image
                import pytesseract
            except ImportError:
                raise ImportError(
                    "To use the 'tesseract' annotator, you need to install 'pytesseract' and 'Pillow'."
                )

    def fit(self, page: pymupdf.Page, table_elements: list[TableElement]) -> Output:
        drawings = page.get_drawings()

        is_not_full_page = partial(self.is_not_full_page_drawing, page=page)
        filtered_drawings = list(filter(is_not_full_page, drawings))

        clusters = page.cluster_drawings(drawings=filtered_drawings)

        is_stroked = partial(self.is_stroked_cluster, drawings=filtered_drawings)
        filtered_clusters = filter(is_stroked, clusters)
        filtered_clusters = list(filter(self.huge_enough_rect, filtered_clusters))

        within_clusters = partial(is_in_rects, rect_list=filtered_clusters)
        filtered_drawings = list(
            filter(lambda p: within_clusters(p["rect"]), filtered_drawings)
        )

        image_info = pymupdf.utils.get_image_info(page)
        image_elements = []
        for img in image_info:
            rect = pymupdf.Rect(img["bbox"])
            if not self.huge_enough_rect(rect):
                continue
            if not self.is_not_full_page_drawing(rect, page):
                continue
            element = self.create_image_element(page, rect, img["number"])
            image_elements.append(element)

        # if cluster is not table, then it is a drawing (e.g. a chart)
        tab_rects = [t.rect for t in table_elements]
        candidate_clusters = list(
            filter(lambda r: not intersects_rects(r, tab_rects), filtered_clusters)
        )
        for i, cluster in enumerate(candidate_clusters):
            element = self.create_image_element(page, cluster, f"diagram-{i}")
            image_elements.append(element)

        return {
            "drawings": filtered_drawings,
            "image_elements": image_elements,
            "clusters": filtered_clusters,
        }

    def create_image_element(
        self, page: pymupdf.Page, rect: pymupdf.Rect, postfix: str
    ) -> ImageElement:
        buffer = None
        if self.write_images is not None or self.annotate_images is not False:
            pix: pymupdf.Pixmap = pymupdf.utils.get_pixmap(
                page, clip=rect, dpi=self.dpi
            )
            buffer = io.BytesIO()
            buffer.write(pix.tobytes())
            del pix

        alt, path = self.save_image_pipeline(buffer, page, postfix)
        annotation = self.annotation_pipeline(buffer, page)

        return ImageElement(rect=rect, alt=alt, path=path, annotation=annotation)

    def save_image_pipeline(
        self, buffer: io.BytesIO | None, page: pymupdf.Page, postfix: str
    ) -> tuple[str, Path | None]:
        if self.write_images is not None and buffer is not None:
            filename = Path(page.parent.name).with_suffix("").name
            path = self.write_images / f"{filename}-{page.number + 1}-{postfix}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(buffer.getvalue())
            return f"{page.number + 1}-{postfix}.png", path
        else:
            return f"{page.number + 1}-{postfix}.png", None

    def annotation_pipeline(
        self, buffer: io.BytesIO | None, page: pymupdf.Page
    ) -> str | None:
        if buffer is None:
            return None

        if self.annotate_images == "tesseract":
            return self.tesseract_pipeline(buffer)

    def tesseract_pipeline(self, buffer: io.BytesIO) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            raise ImportError(
                "To use the 'tesseract' annotator, you need to install 'pytesseract' and 'Pillow'."
            )
        img_tesseract = Image.open(buffer)
        hocr = pytesseract.image_to_pdf_or_hocr(
            img_tesseract, extension="hocr"
        ).decode()
        hocr = re.sub(' xmlns="[^"]+"', "", hocr, count=1)
        hocr_as_xml: ElementTree.Element = ElementTree.fromstring(hocr)
        annotation = []
        for line in hocr_as_xml.iterfind(".//span[@class='ocr_line']"):
            # <span class='ocr_line' id='line_1_25' title="bbox 79 430 642 460; baseline 0.002 -10.007; x_size 21.5;
            # x_descenders 5.5; x_ascenders 5.3333335">
            text_from_words = []
            for word in line.iterfind(".//span[@class='ocrx_word']"):
                # <span class='ocrx_word' id='word_1_303' title='bbox 79 430 92 460; x_wconf 53'>FP</span>
                text_from_words.append(word.text)
            annotation.append(" ".join(text_from_words))
        return "\n".join(annotation)

    @staticmethod
    def is_not_full_page_drawing(
        drawing: dict | pymupdf.Rect, page: pymupdf.Page
    ) -> bool:
        page_clip = page.rect + (36, 36, -36, -36)  # full page graphics

        if isinstance(drawing, dict):
            if (
                drawing["rect"].width < page_clip.width
                or drawing["rect"].height < page_clip.height
            ):
                return True
        else:
            if drawing.width < page_clip.width or drawing.height < page_clip.height:
                return True

        return False

    @staticmethod
    def is_stroked_cluster(cluster: pymupdf.Rect, drawings: list[dict]) -> bool:
        for p in drawings:
            if p["rect"] not in cluster:
                continue
            if p["type"] != "f":
                return True
            for item in p["items"]:
                if item[0] == "c":
                    return True
        return False

    def huge_enough_rect(self, cluster: pymupdf.Rect) -> bool:
        return (
            cluster.width > self.minimal_image_size[0]
            and cluster.height > self.minimal_image_size[1]
        )
