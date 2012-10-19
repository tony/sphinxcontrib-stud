rm -fr _build
sphinx-build -b text -d _build/doctrees . _build/text
diff _build/text/index.txt index_as_built.txt
