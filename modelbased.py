import tabula

dfs = tabula.read_pdf("test.pdf", pages=[6,7,8,12,13,15,16])

tabula.convert_into("test.pdf", "output.csv", output_format="csv", pages=[6])