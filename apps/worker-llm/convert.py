import opendataloader_pdf

# Batch all files in one call — each convert() spawns a JVM process, so repeated calls are slow

opendataloader_pdf.convert(
    input_path=["mock.pdf"],
    output_dir="output/",
    image_output='off',
    format="markdown,json"
)
