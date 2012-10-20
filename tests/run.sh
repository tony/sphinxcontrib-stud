rm -fr _build/
sphinx-build -E -a -b text -d _build/doctrees . _build/text

gl=$@

if [ $# -eq 0 ]
    then gl='*'
fi

for f in _build/text/$gl/index.txt; do
    r=`echo $f | sed 's@^_build/text/test\(.*\)/index.txt@test\1/result.txt@'`
    echo
    echo CHECK: comparing $r and $f
    diff $r $f
    if [ $? -eq 0 ]
        then echo "OK"
    fi
    # Uncomment this to overwrite result files
    #cp -i $f $r
done

# Use this to update result files
# for f in _build/text/*/index.txt; do cp -f $f `echo $f | sed 's@^_build/text/test\(.*\)/index.txt@test\1/result.txt@'`; done
