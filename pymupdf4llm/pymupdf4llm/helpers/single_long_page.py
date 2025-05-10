import pymupdf

class _SingleLongPage:
    
    _doc:pymupdf.Document
          
    def __init__(self, doc:pymupdf.Document, pages_per_row=1):

		# Create source document from supplied pages          
        page_count = doc.page_count
		# Get dimensions of the first page as reference
        first_page = doc[0]
        page_width = first_page.rect.width
        page_height = first_page.rect.height

		# Calculate rows needed
        rows = (page_count + pages_per_row - 1) // pages_per_row  # Ceiling division

		# Create a new PDF with a single page large enough to hold all pages
        # This assumes that all the pages are the same width and height!
        self._doc = pymupdf.open()
        total_width = page_width * min(pages_per_row, page_count)
        total_height = page_height * rows
        
		# note: MuPDF specifically has a limit of about 32,767 × 32,767 points for page size
        if total_height >= 32767:
            raise ValueError("Page height exceeds maximum of 32,767 points")

		# Create a new single page with the calculated dimensions
        single_page = self._doc.new_page(width=total_width, height=total_height)

        # print(f"dst_page.rect.height: {single_page.rect.height}")

		# Copy content from each source page to the appropriate position on the destination page
        for i in range(page_count):
            row = i // pages_per_row
            col = i % pages_per_row

			# Calculate position for this page
            x = col * page_width
            y = row * page_height

			# Get source page
            src_page = doc[i]

            r = pymupdf.Rect(x,y, src_page.rect.width, (y+src_page.rect.height))

			# Copy the content
            single_page.show_pdf_page(r, doc, i)
    
def SingleLongPageDocument(doc:pymupdf.Document, pages_per_row=1) -> pymupdf.Document:
    slp = _SingleLongPage(doc, pages_per_row)
    return slp._doc
